"""Aggregate Root: Fatura + Cobranças.

Fatura é o Aggregate Root que controla o ciclo de vida das cobranças.
Toda mutação de estado (transição de status, adição/pausa/retomada de cobrança)
passa por este aggregate, que enforça invariantes de negócio.

Classe pura de domínio — sem dependência de SQLAlchemy ou infraestrutura.

Example:
    >>> agg = FaturaAggregate.from_primitives(
    ...     id="fat_abc", cliente_id="cli_xyz", valor=100000,
    ...     moeda="BRL", status="pendente", vencimento=datetime.now(),
    ...     descricao=None, numero_nf=None, pagamento_link=None,
    ...     pago_em=None, promessa_pagamento=None,
    ... )
    >>> agg.transicionar(FaturaStatus.PAGO)
    >>> agg.status == FaturaStatus.PAGO
    True
    >>> agg.pago_em is not None
    True
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.domain.events.base import DomainEvent
from app.domain.events.fatura_events import FaturaVenceu, PagamentoConfirmado
from app.domain.value_objects.cobranca_enums import CobrancaStatus
from app.domain.value_objects.fatura_status import FaturaStatus
from app.exceptions import APIError


@dataclass
class CobrancaData:
    """Representação de dados de cobrança dentro do aggregate boundary.

    Dataclass simples (não é entidade ORM). O aggregate manipula estes
    objetos para enforçar invariantes sem depender de SQLAlchemy.
    """

    id: str
    fatura_id: str
    cliente_id: str
    tipo: str
    canal: str
    mensagem: str | None
    tom: str | None
    status: str
    pausado: bool
    agent_decision_id: str | None
    enviado_em: datetime | None


@dataclass
class FaturaAggregate:
    """Aggregate Root para Fatura + Cobranças.

    Invariantes enforçadas:
        1. Fatura terminal (pago/cancelado) não aceita novas cobranças.
        2. Transição de status só via ``transicionar()``.
        3. Pausar/retomar cobrança respeita status da fatura.
        4. ``pago_em`` preenchido automaticamente ao transicionar para PAGO.

    Attributes:
        id: Identificador único (prefixo fat_).
        cliente_id: FK para o cliente (prefixo cli_).
        valor: Valor em centavos (>= 0).
        moeda: Código ISO 4217 (default BRL).
        status: Status atual como FaturaStatus enum.
        vencimento: Data de vencimento (timezone-aware).
        cobrancas: Lista de cobranças associadas.
    """

    id: str
    cliente_id: str
    valor: int
    moeda: str
    status: FaturaStatus
    vencimento: datetime
    descricao: str | None
    numero_nf: str | None
    pagamento_link: str | None
    pago_em: datetime | None
    promessa_pagamento: datetime | None
    cobrancas: list[CobrancaData] = field(default_factory=list)
    _events: list[DomainEvent] = field(default_factory=list, repr=False)

    def collect_events(self) -> list[DomainEvent]:
        """Retorna eventos acumulados e limpa a lista interna."""
        events = list(self._events)
        self._events.clear()
        return events

    @classmethod
    def from_primitives(
        cls,
        *,
        id: str,
        cliente_id: str,
        valor: int,
        moeda: str,
        status: str,
        vencimento: datetime,
        descricao: str | None = None,
        numero_nf: str | None = None,
        pagamento_link: str | None = None,
        pago_em: datetime | None = None,
        promessa_pagamento: datetime | None = None,
        cobrancas: list[dict] | None = None,
    ) -> FaturaAggregate:
        """Constrói aggregate a partir de dados primitivos (ex: SQLAlchemy model).

        Args:
            cobrancas: Lista de dicts com campos de CobrancaData.
        """
        return cls(
            id=id,
            cliente_id=cliente_id,
            valor=valor,
            moeda=moeda,
            status=FaturaStatus(status),
            vencimento=vencimento,
            descricao=descricao,
            numero_nf=numero_nf,
            pagamento_link=pagamento_link,
            pago_em=pago_em,
            promessa_pagamento=promessa_pagamento,
            cobrancas=[CobrancaData(**c) for c in (cobrancas or [])],
        )

    @property
    def is_terminal(self) -> bool:
        """True se fatura em estado terminal (pago ou cancelado)."""
        return self.status.is_terminal

    def transicionar(self, novo_status: FaturaStatus) -> None:
        """Transiciona status da fatura.

        Raises:
            APIError(409): Se a transição for inválida pela máquina de estados.
        """
        if not self.status.pode_transicionar_para(novo_status):
            allowed = [s.value for s in self.status.transicoes_validas]
            raise APIError(
                409,
                "transicao-invalida",
                "Transição de status inválida",
                f"Não é possível mudar de '{self.status.value}' para "
                f"'{novo_status.value}'. "
                f"Transições permitidas: {allowed or 'nenhuma (status terminal)'}.",
            )
        self.status = novo_status
        if novo_status == FaturaStatus.PAGO:
            self.pago_em = datetime.now(timezone.utc)

        # Emitir domain events
        if novo_status == FaturaStatus.VENCIDO:
            now = datetime.now(timezone.utc)
            venc = self.vencimento
            if venc.tzinfo is None:
                venc = venc.replace(tzinfo=timezone.utc)
            dias = max(0, (now - venc).days)
            self._events.append(
                FaturaVenceu(
                    fatura_id=self.id,
                    cliente_id=self.cliente_id,
                    valor_centavos=self.valor,
                    dias_atraso=dias,
                )
            )
        elif novo_status == FaturaStatus.PAGO:
            self._events.append(
                PagamentoConfirmado(
                    fatura_id=self.id,
                    cliente_id=self.cliente_id,
                    valor_centavos=self.valor,
                    meio_pagamento="",  # Preenchido pelo service quando disponível
                )
            )

    def pode_receber_cobranca(self) -> bool:
        """Verifica se a fatura aceita novas cobranças (não terminal)."""
        return not self.is_terminal

    def adicionar_cobranca(self, cobranca: CobrancaData) -> None:
        """Adiciona cobrança ao aggregate.

        Raises:
            APIError(409): Se a fatura estiver em status terminal.
        """
        if not self.pode_receber_cobranca():
            raise APIError(
                409,
                "fatura-terminal",
                "Fatura em status terminal",
                f"Fatura {self.id} está '{self.status.value}' e não aceita novas cobranças.",
            )
        self.cobrancas.append(cobranca)

    def pausar_cobranca(self, cobranca_id: str) -> CobrancaData:
        """Pausa uma cobrança do aggregate.

        Returns:
            A CobrancaData atualizada com status=pausado.

        Raises:
            APIError(404): Se a cobrança não pertencer a esta fatura.
        """
        cob = self._find_cobranca(cobranca_id)
        cob.pausado = True
        cob.status = CobrancaStatus.PAUSADO.value
        return cob

    def retomar_cobranca(self, cobranca_id: str) -> CobrancaData:
        """Retoma uma cobrança pausada.

        Raises:
            APIError(409): Se a fatura estiver em status terminal.
            APIError(404): Se a cobrança não pertencer a esta fatura.
        """
        if self.is_terminal:
            raise APIError(
                409,
                "fatura-terminal",
                "Fatura em status terminal",
                f"Não é possível retomar cobranças de fatura '{self.status.value}'.",
            )
        cob = self._find_cobranca(cobranca_id)
        cob.pausado = False
        cob.status = CobrancaStatus.ENVIADO.value
        return cob

    def _find_cobranca(self, cobranca_id: str) -> CobrancaData:
        """Busca cobrança por ID dentro do aggregate.

        Raises:
            APIError(404): Se não encontrada.
        """
        for c in self.cobrancas:
            if c.id == cobranca_id:
                return c
        raise APIError(
            404,
            "cobranca-nao-encontrada",
            "Cobrança não encontrada",
            f"Cobrança {cobranca_id} não pertence à fatura {self.id}.",
        )
