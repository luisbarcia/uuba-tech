"""Motor da régua de cobrança automática.

Processa faturas vencidas, identifica próximo passo da régua,
aplica compliance e registra cobranças.
"""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.events.event_bus import EventBus
from app.domain.events.fatura_events import CobrancaEnviada
from app.models.cobranca import Cobranca
from app.models.fatura import Fatura
from app.models.regua import Regua, ReguaPasso
from app.services.compliance import is_horario_util, pode_enviar
from app.utils.ids import generate_id


async def processar_regua(
    session: AsyncSession,
    event_bus: EventBus | None = None,
    agora: datetime | None = None,
) -> dict:
    """Executa um ciclo da régua de cobrança.

    Returns:
        Dict com contadores: faturas_processadas, cobrancas_criadas, bloqueadas_compliance.
    """
    if agora is None:
        agora = datetime.now(timezone.utc)

    # Buscar régua ativa
    result = await session.execute(select(Regua).where(Regua.ativa.is_(True)).limit(1))
    regua = result.scalar_one_or_none()
    if not regua:
        return {
            "faturas_processadas": 0,
            "cobrancas_criadas": 0,
            "bloqueadas_compliance": 0,
            "erro": "Nenhuma régua ativa encontrada",
        }

    # Buscar faturas vencidas
    result = await session.execute(select(Fatura).where(Fatura.status == "vencido"))
    faturas_vencidas = result.scalars().all()

    cobrancas_criadas = 0
    bloqueadas = 0

    for fatura in faturas_vencidas:
        venc = fatura.vencimento
        if venc.tzinfo is None:
            venc = venc.replace(tzinfo=timezone.utc)
        dias_atraso = max(0, (agora - venc).days)

        # Determinar próximo passo
        passo = _proximo_passo(regua.passos, dias_atraso)
        if not passo:
            continue

        # Verificar se este passo já foi executado
        result = await session.execute(
            select(Cobranca).where(
                Cobranca.fatura_id == fatura.id,
                Cobranca.tipo == passo.tipo,
                Cobranca.tom == passo.tom,
            )
        )
        if result.scalar_one_or_none():
            continue  # Passo já executado

        # Check compliance: horário
        if not is_horario_util(agora):
            bloqueadas += 1
            continue

        # Check compliance: frequência
        result = await session.execute(
            select(Cobranca.enviado_em).where(
                Cobranca.cliente_id == fatura.cliente_id,
                Cobranca.enviado_em.isnot(None),
            )
        )
        datas_recentes = [row[0] for row in result.all() if row[0] is not None]
        if not pode_enviar(datas_recentes, agora=agora):
            bloqueadas += 1
            continue

        # Renderizar mensagem
        mensagem = _renderizar_template(passo.template_mensagem, fatura, dias_atraso)

        # Criar cobrança
        cobranca = Cobranca(
            id=generate_id("cob"),
            fatura_id=fatura.id,
            cliente_id=fatura.cliente_id,
            tipo=passo.tipo,
            canal=passo.canal,
            mensagem=mensagem,
            tom=passo.tom,
            status="enviado",
            pausado=False,
            agent_decision_id=None,
            enviado_em=agora,
        )
        session.add(cobranca)
        cobrancas_criadas += 1

        # Emitir evento
        if event_bus:
            await event_bus.publish(
                CobrancaEnviada(
                    cobranca_id=cobranca.id,
                    fatura_id=fatura.id,
                    cliente_id=fatura.cliente_id,
                    canal=passo.canal,
                    tom=passo.tom,
                )
            )

    await session.commit()

    return {
        "faturas_processadas": len(faturas_vencidas),
        "cobrancas_criadas": cobrancas_criadas,
        "bloqueadas_compliance": bloqueadas,
    }


def _proximo_passo(passos: list[ReguaPasso], dias_atraso: int) -> ReguaPasso | None:
    """Retorna o passo mais avançado aplicável para os dias de atraso."""
    aplicaveis = [p for p in passos if p.dias_atraso <= dias_atraso]
    if not aplicaveis:
        return None
    return max(aplicaveis, key=lambda p: p.dias_atraso)


def _renderizar_template(template: str, fatura: Fatura, dias_atraso: int) -> str:
    """Substitui variáveis no template da mensagem."""
    valor_reais = f"{fatura.valor / 100:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    venc = fatura.vencimento
    if venc:
        venc_fmt = venc.strftime("%d/%m/%Y")
    else:
        venc_fmt = ""

    return template.format(
        numero_nf=fatura.numero_nf or "S/N",
        valor=valor_reais,
        vencimento=venc_fmt,
        dias_atraso=dias_atraso,
        link_pagamento=fatura.pagamento_link or "(link pendente)",
    )
