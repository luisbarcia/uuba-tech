"""tenant_id NOT NULL: constraint + FK em clientes, faturas, cobrancas

Revision ID: 004
Revises: 003
Create Date: 2026-03-28

Fase B da migracao. Requer que 003 tenha sido aplicada com sucesso
(zero registros com tenant_id NULL).

Adiciona NOT NULL constraint e FK para tenants.id nas 3 tabelas.
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()

    # Safety check: zero NULLs antes de aplicar NOT NULL
    for table in ("clientes", "faturas", "cobrancas"):
        result = conn.execute(
            sa.text(f"SELECT COUNT(*) FROM {table} WHERE tenant_id IS NULL")
        ).scalar()
        if result > 0:
            raise RuntimeError(
                f"ABORT: {table} tem {result} registros com tenant_id NULL. "
                f"Rode a migracao 003 primeiro."
            )

    # NOT NULL constraints
    op.alter_column("clientes", "tenant_id", existing_type=sa.String(20), nullable=False)
    op.alter_column("faturas", "tenant_id", existing_type=sa.String(20), nullable=False)
    op.alter_column("cobrancas", "tenant_id", existing_type=sa.String(20), nullable=False)

    # FK constraints
    op.create_foreign_key("fk_clientes_tenant", "clientes", "tenants", ["tenant_id"], ["id"])
    op.create_foreign_key("fk_faturas_tenant", "faturas", "tenants", ["tenant_id"], ["id"])
    op.create_foreign_key("fk_cobrancas_tenant", "cobrancas", "tenants", ["tenant_id"], ["id"])


def downgrade() -> None:
    # Remover FKs
    op.drop_constraint("fk_cobrancas_tenant", "cobrancas", type_="foreignkey")
    op.drop_constraint("fk_faturas_tenant", "faturas", type_="foreignkey")
    op.drop_constraint("fk_clientes_tenant", "clientes", type_="foreignkey")

    # Voltar para nullable
    op.alter_column("cobrancas", "tenant_id", existing_type=sa.String(20), nullable=True)
    op.alter_column("faturas", "tenant_id", existing_type=sa.String(20), nullable=True)
    op.alter_column("clientes", "tenant_id", existing_type=sa.String(20), nullable=True)
