"""Eventos de domínio relacionados a Faturas e Cobranças.

Cada evento representa um fato que já aconteceu no domínio de negócio.
São imutáveis (frozen dataclass) e carregam apenas os dados essenciais.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.domain.events.base import DomainEvent


@dataclass(frozen=True)
class FaturaVenceu(DomainEvent):
    """Emitido quando uma fatura transiciona para status 'vencido'.

    Consumidores futuros: Régua de cobrança, Scoring.
    """

    fatura_id: str = ""
    cliente_id: str = ""
    valor_centavos: int = 0
    dias_atraso: int = 0


@dataclass(frozen=True)
class PagamentoConfirmado(DomainEvent):
    """Emitido quando uma fatura transiciona para status 'pago'.

    Consumidores futuros: Régua (pausar), Bot (agradecimento), Dashboard.
    """

    fatura_id: str = ""
    cliente_id: str = ""
    valor_centavos: int = 0
    meio_pagamento: str = ""


@dataclass(frozen=True)
class CobrancaEnviada(DomainEvent):
    """Emitido quando uma cobrança é registrada/enviada.

    Consumidores futuros: Dashboard, Audit Trail.
    """

    cobranca_id: str = ""
    fatura_id: str = ""
    cliente_id: str = ""
    canal: str = ""
    tom: str = ""


@dataclass(frozen=True)
class PromessaRegistrada(DomainEvent):
    """Emitido quando um cliente faz promessa de pagamento.

    Consumidores futuros: Follow-up scheduler.
    """

    fatura_id: str = ""
    cliente_id: str = ""
    data_promessa: datetime | None = None


@dataclass(frozen=True)
class EscalacaoSolicitada(DomainEvent):
    """Emitido quando atendimento precisa ser escalado.

    Consumidores futuros: Integração Chatwoot.
    """

    fatura_id: str = ""
    cliente_id: str = ""
    motivo: str = ""
