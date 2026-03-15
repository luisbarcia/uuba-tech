"""initial schema: clientes, faturas, cobrancas

Revision ID: 001
Revises:
Create Date: 2026-03-15
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'clientes',
        sa.Column('id', sa.String(20), primary_key=True),
        sa.Column('nome', sa.String(255), nullable=False),
        sa.Column('documento', sa.String(14), nullable=False),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('telefone', sa.String(20), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_clientes_telefone', 'clientes', ['telefone'])
    op.create_index('ix_clientes_documento', 'clientes', ['documento'], unique=True)

    op.create_table(
        'faturas',
        sa.Column('id', sa.String(20), primary_key=True),
        sa.Column('cliente_id', sa.String(20), sa.ForeignKey('clientes.id'), nullable=False),
        sa.Column('valor', sa.Integer(), nullable=False),
        sa.Column('moeda', sa.String(3), nullable=False, server_default='BRL'),
        sa.Column('status', sa.String(20), nullable=False, server_default='pendente'),
        sa.Column('vencimento', sa.DateTime(timezone=True), nullable=False),
        sa.Column('descricao', sa.String(500), nullable=True),
        sa.Column('numero_nf', sa.String(50), nullable=True),
        sa.Column('pagamento_link', sa.String(500), nullable=True),
        sa.Column('pago_em', sa.DateTime(timezone=True), nullable=True),
        sa.Column('promessa_pagamento', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_faturas_status', 'faturas', ['status'])
    op.create_index('ix_faturas_vencimento', 'faturas', ['vencimento'])
    op.create_index('ix_faturas_cliente_id', 'faturas', ['cliente_id'])

    op.create_table(
        'cobrancas',
        sa.Column('id', sa.String(20), primary_key=True),
        sa.Column('fatura_id', sa.String(20), sa.ForeignKey('faturas.id'), nullable=False),
        sa.Column('cliente_id', sa.String(20), sa.ForeignKey('clientes.id'), nullable=False),
        sa.Column('tipo', sa.String(30), nullable=False),
        sa.Column('canal', sa.String(20), nullable=False, server_default='whatsapp'),
        sa.Column('mensagem', sa.Text(), nullable=True),
        sa.Column('tom', sa.String(30), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='enviado'),
        sa.Column('pausado', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('agent_decision_id', sa.String(20), nullable=True),
        sa.Column('enviado_em', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_cobrancas_fatura_id', 'cobrancas', ['fatura_id'])
    op.create_index('ix_cobrancas_cliente_id', 'cobrancas', ['cliente_id'])


def downgrade() -> None:
    op.drop_table('cobrancas')
    op.drop_table('faturas')
    op.drop_table('clientes')
