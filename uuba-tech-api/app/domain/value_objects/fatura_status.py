from __future__ import annotations

from enum import Enum


class FaturaStatus(Enum):
    """Status de uma fatura com máquina de estados embutida.

    Transições válidas:
        pendente  → pago, vencido, cancelado
        vencido   → pago, cancelado
        pago      → (terminal)
        cancelado → (terminal)
    """

    PENDENTE = "pendente"
    VENCIDO = "vencido"
    PAGO = "pago"
    CANCELADO = "cancelado"

    _TRANSITIONS: dict[str, list[str]] = {  # type: ignore[assignment]
        "pendente": ["pago", "vencido", "cancelado"],
        "vencido": ["pago", "cancelado"],
        "pago": [],
        "cancelado": [],
    }

    def pode_transicionar_para(self, novo: FaturaStatus) -> bool:
        """Verifica se a transição para o novo status é permitida."""
        allowed = self._TRANSITIONS.value.get(self.value, [])
        return novo.value in allowed

    @property
    def is_terminal(self) -> bool:
        """Retorna True se o status é terminal (sem transições possíveis)."""
        return len(self._TRANSITIONS.value.get(self.value, [])) == 0

    @property
    def transicoes_validas(self) -> list[FaturaStatus]:
        """Lista de status para os quais é possível transicionar."""
        return [FaturaStatus(v) for v in self._TRANSITIONS.value.get(self.value, [])]
