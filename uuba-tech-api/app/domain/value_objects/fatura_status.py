"""Value Object para status de fatura com máquina de estados embutida.

Define os estados possíveis de uma fatura e as transições válidas entre eles.
Substitui o dict FATURA_TRANSITIONS que antes vivia em fatura_service.py.

Example:
    >>> status = FaturaStatus("pendente")
    >>> status.pode_transicionar_para(FaturaStatus.PAGO)
    True
    >>> FaturaStatus.PAGO.is_terminal
    True
"""

from __future__ import annotations

from enum import Enum


_FATURA_TRANSITIONS: dict[str, list[str]] = {
    "pendente": ["pago", "vencido", "cancelado"],
    "vencido": ["pago", "cancelado"],
    "pago": [],
    "cancelado": [],
}


class FaturaStatus(Enum):
    """Status de uma fatura com máquina de estados embutida.

    Cada membro do enum representa um estado possível. As transições válidas
    são definidas no módulo (``_FATURA_TRANSITIONS``), fora do Enum para
    não contaminar ``list(FaturaStatus)`` com membros espúrios.

    Attributes:
        PENDENTE: Fatura criada, aguardando vencimento ou pagamento.
        VENCIDO: Fatura com data de vencimento ultrapassada.
        PAGO: Pagamento confirmado. Estado terminal.
        CANCELADO: Fatura cancelada. Estado terminal.

    Transições válidas::

        pendente  → pago, vencido, cancelado
        vencido   → pago, cancelado
        pago      → (terminal)
        cancelado → (terminal)

    Example:
        >>> current = FaturaStatus.PENDENTE
        >>> current.pode_transicionar_para(FaturaStatus.VENCIDO)
        True
        >>> list(FaturaStatus)  # apenas 4 membros, sem contaminação
        [<FaturaStatus.PENDENTE: 'pendente'>, ...]
    """

    PENDENTE = "pendente"
    VENCIDO = "vencido"
    PAGO = "pago"
    CANCELADO = "cancelado"

    def pode_transicionar_para(self, novo: FaturaStatus) -> bool:
        """Verifica se a transição para o novo status é permitida.

        Args:
            novo: Status de destino desejado.

        Returns:
            True se a transição é válida, False caso contrário.

        Example:
            >>> FaturaStatus.PENDENTE.pode_transicionar_para(FaturaStatus.PAGO)
            True
            >>> FaturaStatus.PAGO.pode_transicionar_para(FaturaStatus.PENDENTE)
            False
        """
        allowed = _FATURA_TRANSITIONS.get(self.value, [])
        return novo.value in allowed

    @property
    def is_terminal(self) -> bool:
        """Retorna True se o status é terminal (sem transições possíveis).

        Estados terminais: PAGO, CANCELADO.

        Example:
            >>> FaturaStatus.PAGO.is_terminal
            True
            >>> FaturaStatus.PENDENTE.is_terminal
            False
        """
        return len(_FATURA_TRANSITIONS.get(self.value, [])) == 0

    @property
    def transicoes_validas(self) -> list[FaturaStatus]:
        """Lista de status para os quais é possível transicionar.

        Returns:
            Lista de FaturaStatus válidos como destino. Vazia para terminais.

        Example:
            >>> FaturaStatus.VENCIDO.transicoes_validas
            [<FaturaStatus.PAGO: 'pago'>, <FaturaStatus.CANCELADO: 'cancelado'>]
        """
        return [FaturaStatus(v) for v in _FATURA_TRANSITIONS.get(self.value, [])]
