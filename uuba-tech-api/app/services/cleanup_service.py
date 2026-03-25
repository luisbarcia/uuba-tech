"""Serviço de limpeza de dados (LGPD Art. 15/16).

Job que anonimiza dados expirados conforme política de retenção.
"""

from datetime import datetime, timezone, timedelta

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.cliente import Cliente
from app.models.cobranca import Cobranca
from app.models.fatura import Fatura


async def executar_cleanup(session: AsyncSession) -> dict:
    """Executa limpeza de dados conforme política de retenção LGPD.

    Returns:
        Dict com contadores: mensagens_limpas, clientes_anonimizados.
    """
    now = datetime.now(timezone.utc)
    mensagens_limpas = await _limpar_mensagens_antigas(session, now)
    clientes_anonimizados = await _anonimizar_clientes_inativos(session, now)
    await session.commit()
    return {
        "mensagens_limpas": mensagens_limpas,
        "clientes_anonimizados": clientes_anonimizados,
        "executado_em": now.isoformat(),
    }


async def _limpar_mensagens_antigas(session: AsyncSession, now: datetime) -> int:
    """Remove mensagens de cobranças de faturas resolvidas há mais de N anos."""
    cutoff = now - timedelta(days=settings.retencao_mensagens_anos * 365)

    # Faturas resolvidas (pago/cancelado) antes do cutoff
    faturas_resolvidas = select(Fatura.id).where(
        Fatura.status.in_(["pago", "cancelado"]),
        Fatura.updated_at < cutoff,
    )

    result = await session.execute(
        update(Cobranca)
        .where(
            Cobranca.fatura_id.in_(faturas_resolvidas),
            Cobranca.mensagem.isnot(None),
        )
        .values(mensagem=None)
    )
    return result.rowcount


async def _anonimizar_clientes_inativos(session: AsyncSession, now: datetime) -> int:
    """Anonimiza clientes sem faturas ativas há mais de N anos."""
    import hashlib

    cutoff = now - timedelta(days=settings.retencao_clientes_inativos_anos * 365)

    # Clientes com todas as faturas resolvidas e última atividade antes do cutoff
    clientes_ativos_ids = (
        select(Fatura.cliente_id).where(Fatura.status.in_(["pendente", "vencido"])).distinct()
    )

    result = await session.execute(
        select(Cliente).where(
            Cliente.deletado_em.is_(None),
            Cliente.updated_at < cutoff,
            Cliente.id.notin_(clientes_ativos_ids),
        )
    )
    clientes = result.scalars().all()

    for cliente in clientes:
        doc_hash = hashlib.sha256(cliente.documento.encode()).hexdigest()[:14]
        cliente.nome = "REMOVIDO"
        cliente.documento = doc_hash
        cliente.email = None
        cliente.telefone = None
        cliente.deletado_em = now

    return len(clientes)
