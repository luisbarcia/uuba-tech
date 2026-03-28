"""backfill tenant_id: atribuir tenant legado a registros orfaos + dropar indice antigo

Revision ID: 003
Revises: 002
Create Date: 2026-03-28

Fase A da migracao NOT NULL de tenant_id.
Backfill orfaos em clientes/faturas/cobrancas com tenant legado,
depois remove indice unico de documento sem tenant (ix_clientes_documento)
que bloqueia multi-tenancy real.

Cria indice composto (tenant_id, documento) UNIQUE se nao existir.
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from datetime import datetime, timezone

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

LEGACY_TENANT_ID = "ten_legacy"


def upgrade() -> None:
    conn = op.get_bind()

    # Criar tenant legado se nao existir
    exists = conn.execute(
        sa.text("SELECT 1 FROM tenants WHERE id = :id"), {"id": LEGACY_TENANT_ID}
    ).fetchone()

    if not exists:
        now = datetime.now(timezone.utc).isoformat()
        conn.execute(
            sa.text(
                "INSERT INTO tenants (id, nome, slug, ativo, plan, created_at, updated_at) "
                "VALUES (:id, :nome, :slug, :ativo, :plan, :created_at, :updated_at)"
            ),
            {
                "id": LEGACY_TENANT_ID,
                "nome": "Tenant Legado (migração)",
                "slug": "legacy",
                "ativo": True,
                "plan": "starter",
                "created_at": now,
                "updated_at": now,
            },
        )

    # Backfill: clientes sem tenant_id → ten_legacy
    conn.execute(
        sa.text("UPDATE clientes SET tenant_id = :tid WHERE tenant_id IS NULL"),
        {"tid": LEGACY_TENANT_ID},
    )

    # Backfill: faturas — inferir do cliente, fallback para ten_legacy
    conn.execute(
        sa.text(
            "UPDATE faturas SET tenant_id = ("
            "  SELECT tenant_id FROM clientes WHERE clientes.id = faturas.cliente_id"
            ") WHERE tenant_id IS NULL AND EXISTS ("
            "  SELECT 1 FROM clientes WHERE clientes.id = faturas.cliente_id AND clientes.tenant_id IS NOT NULL"
            ")"
        )
    )
    conn.execute(
        sa.text("UPDATE faturas SET tenant_id = :tid WHERE tenant_id IS NULL"),
        {"tid": LEGACY_TENANT_ID},
    )

    # Backfill: cobrancas — inferir da fatura→cliente, fallback para ten_legacy
    conn.execute(
        sa.text(
            "UPDATE cobrancas SET tenant_id = ("
            "  SELECT tenant_id FROM faturas WHERE faturas.id = cobrancas.fatura_id"
            ") WHERE tenant_id IS NULL AND EXISTS ("
            "  SELECT 1 FROM faturas WHERE faturas.id = cobrancas.fatura_id AND faturas.tenant_id IS NOT NULL"
            ")"
        )
    )
    conn.execute(
        sa.text("UPDATE cobrancas SET tenant_id = :tid WHERE tenant_id IS NULL"),
        {"tid": LEGACY_TENANT_ID},
    )

    # Dropar indice antigo (documento UNIQUE sem tenant) — bloqueia multi-tenancy
    op.drop_index("ix_clientes_documento", "clientes")

    # Criar indice composto (tenant_id, documento) UNIQUE se nao existir
    # Nota: 002 ja pode ter criado ix_clientes_tenant_documento — ignorar erro
    try:
        op.create_index(
            "ix_clientes_tenant_documento", "clientes", ["tenant_id", "documento"], unique=True
        )
    except Exception:
        pass  # Indice ja existe da 002 ou do model


def downgrade() -> None:
    # Recriar indice antigo
    op.create_index("ix_clientes_documento", "clientes", ["documento"], unique=True)

    # Nao reverter o backfill — dados foram modificados irreversivelmente
    # O tenant legado fica no banco
