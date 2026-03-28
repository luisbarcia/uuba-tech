"""optimize indexes: compostos com tenant_id para multi-tenancy

Revision ID: 005
Revises: 004
Create Date: 2026-03-28

Substitui indexes simples por compostos (tenant_id, coluna) para
eliminar filter steps em queries multi-tenant. Adiciona indexes
faltantes para query patterns dos repositories.
"""

from typing import Sequence, Union
from alembic import op

revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- clientes ---

    # telefone: trocar index simples por composto com tenant_id
    op.drop_index("ix_clientes_telefone", "clientes")
    op.create_index("ix_clientes_tenant_telefone", "clientes", ["tenant_id", "telefone"])

    # nome: ORDER BY nome com tenant_id filter
    op.create_index("ix_clientes_tenant_nome", "clientes", ["tenant_id", "nome"])

    # --- faturas ---

    # status: trocar index simples por composto com tenant_id
    op.drop_index("ix_faturas_status", "faturas")
    op.create_index("ix_faturas_tenant_status", "faturas", ["tenant_id", "status"])

    # vencimento: composto para bulk_transicionar_vencidas (status + vencimento)
    op.drop_index("ix_faturas_vencimento", "faturas")
    op.create_index(
        "ix_faturas_tenant_status_vencimento",
        "faturas",
        ["tenant_id", "status", "vencimento"],
    )

    # cliente_id: composto com tenant_id
    op.drop_index("ix_faturas_cliente_id", "faturas")
    op.create_index("ix_faturas_tenant_cliente", "faturas", ["tenant_id", "cliente_id"])

    # numero_nf + cliente_id: dedup para import CSV
    op.create_index(
        "ix_faturas_tenant_nf_cliente",
        "faturas",
        ["tenant_id", "numero_nf", "cliente_id"],
    )

    # --- cobrancas ---

    # fatura_id: composto com tenant_id
    op.drop_index("ix_cobrancas_fatura_id", "cobrancas")
    op.create_index("ix_cobrancas_tenant_fatura", "cobrancas", ["tenant_id", "fatura_id"])

    # cliente_id: composto com tenant_id
    op.drop_index("ix_cobrancas_cliente_id", "cobrancas")
    op.create_index("ix_cobrancas_tenant_cliente", "cobrancas", ["tenant_id", "cliente_id"])

    # created_at DESC: para listagem ordenada por tenant
    op.create_index(
        "ix_cobrancas_tenant_created",
        "cobrancas",
        ["tenant_id", "created_at"],
    )

    # --- webhooks ---

    op.create_index("ix_webhooks_tenant_id", "webhooks", ["tenant_id"])


def downgrade() -> None:
    # --- webhooks ---
    op.drop_index("ix_webhooks_tenant_id", "webhooks")

    # --- cobrancas ---
    op.drop_index("ix_cobrancas_tenant_created", "cobrancas")
    op.drop_index("ix_cobrancas_tenant_cliente", "cobrancas")
    op.create_index("ix_cobrancas_cliente_id", "cobrancas", ["cliente_id"])
    op.drop_index("ix_cobrancas_tenant_fatura", "cobrancas")
    op.create_index("ix_cobrancas_fatura_id", "cobrancas", ["fatura_id"])

    # --- faturas ---
    op.drop_index("ix_faturas_tenant_nf_cliente", "faturas")
    op.drop_index("ix_faturas_tenant_cliente", "faturas")
    op.create_index("ix_faturas_cliente_id", "faturas", ["cliente_id"])
    op.drop_index("ix_faturas_tenant_status_vencimento", "faturas")
    op.create_index("ix_faturas_vencimento", "faturas", ["vencimento"])
    op.drop_index("ix_faturas_tenant_status", "faturas")
    op.create_index("ix_faturas_status", "faturas", ["status"])

    # --- clientes ---
    op.drop_index("ix_clientes_tenant_nome", "clientes")
    op.drop_index("ix_clientes_tenant_telefone", "clientes")
    op.create_index("ix_clientes_telefone", "clientes", ["telefone"])
