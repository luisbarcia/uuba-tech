"""multi-tenancy: tenants, audit_log, reguas, tenant_id em tabelas existentes

Revision ID: 002
Revises: 001
Create Date: 2026-03-26
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Novas tabelas ---

    op.create_table(
        'tenants',
        sa.Column('id', sa.String(20), primary_key=True),
        sa.Column('nome', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(255), nullable=False, server_default=''),
        sa.Column('documento', sa.String(14), nullable=True),
        sa.Column('api_key', sa.String(100), nullable=True),  # legacy (Unkey)
        sa.Column('ativo', sa.Boolean, nullable=False, server_default=sa.text('true')),
        sa.Column('plan', sa.String(20), nullable=False, server_default='starter'),
        sa.Column('conta_azul_client_id', sa.String(255), nullable=True),
        sa.Column('conta_azul_client_secret', sa.Text, nullable=True),
        sa.Column('conta_azul_access_token', sa.Text, nullable=True),
        sa.Column('conta_azul_refresh_token', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_tenants_slug', 'tenants', ['slug'], unique=True)

    op.create_table(
        'audit_log',
        sa.Column('id', sa.String(20), primary_key=True),
        sa.Column('tenant_id', sa.String(20), nullable=False),
        sa.Column('acao', sa.String(30), nullable=False),
        sa.Column('recurso', sa.String(30), nullable=False),
        sa.Column('recurso_id', sa.String(20), nullable=True),
        sa.Column('detalhes', sa.Text, nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_audit_log_tenant_id', 'audit_log', ['tenant_id'])

    op.create_table(
        'reguas',
        sa.Column('id', sa.String(20), primary_key=True),
        sa.Column('tenant_id', sa.String(20), nullable=False),
        sa.Column('nome', sa.String(100), nullable=False),
        sa.Column('ativa', sa.Boolean, nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_reguas_tenant_id', 'reguas', ['tenant_id'])

    op.create_table(
        'regua_passos',
        sa.Column('id', sa.String(20), primary_key=True),
        sa.Column('regua_id', sa.String(20), sa.ForeignKey('reguas.id'), nullable=False),
        sa.Column('ordem', sa.Integer, nullable=False),
        sa.Column('dias_atraso', sa.Integer, nullable=False),
        sa.Column('tipo', sa.String(30), nullable=False),
        sa.Column('canal', sa.String(20), nullable=False, server_default='whatsapp'),
        sa.Column('tom', sa.String(30), nullable=False),
        sa.Column('template_mensagem', sa.Text, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )

    # --- Colunas novas em tabelas existentes ---

    op.add_column('clientes', sa.Column('tenant_id', sa.String(20), nullable=True))
    op.add_column('clientes', sa.Column('deletado_em', sa.DateTime(timezone=True), nullable=True))
    op.create_index('ix_clientes_tenant_id', 'clientes', ['tenant_id'])

    op.add_column('faturas', sa.Column('tenant_id', sa.String(20), nullable=True))
    op.create_index('ix_faturas_tenant_id', 'faturas', ['tenant_id'])

    op.add_column('cobrancas', sa.Column('tenant_id', sa.String(20), nullable=True))
    op.create_index('ix_cobrancas_tenant_id', 'cobrancas', ['tenant_id'])


def downgrade() -> None:
    op.drop_index('ix_cobrancas_tenant_id', 'cobrancas')
    op.drop_column('cobrancas', 'tenant_id')

    op.drop_index('ix_faturas_tenant_id', 'faturas')
    op.drop_column('faturas', 'tenant_id')

    op.drop_index('ix_clientes_tenant_id', 'clientes')
    op.drop_column('clientes', 'deletado_em')
    op.drop_column('clientes', 'tenant_id')

    op.drop_table('regua_passos')
    op.drop_table('reguas')
    op.drop_table('audit_log')
    op.drop_index('ix_tenants_slug', 'tenants')
    op.drop_table('tenants')
