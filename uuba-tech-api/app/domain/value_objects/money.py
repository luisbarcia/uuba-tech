from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from functools import total_ordering


@total_ordering
@dataclass(frozen=True)
class Money:
    """Value Object para valores monetários em centavos.

    Imutável, hashable, comparável. Operações aritméticas retornam novos Money.
    """

    centavos: int
    moeda: str = "BRL"

    def __post_init__(self) -> None:
        if self.centavos < 0:
            raise ValueError(f"Valor não pode ser negativo: {self.centavos}")

    @classmethod
    def zero(cls, moeda: str = "BRL") -> Money:
        return cls(centavos=0, moeda=moeda)

    @property
    def reais(self) -> Decimal:
        return Decimal(self.centavos) / Decimal(100)

    @property
    def is_zero(self) -> bool:
        return self.centavos == 0

    @property
    def formatado(self) -> str:
        reais = self.centavos / 100
        formatado = f"{reais:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"R$ {formatado}"

    def _check_moeda(self, other: Money) -> None:
        if self.moeda != other.moeda:
            raise ValueError(f"Não é possível operar {self.moeda} com {other.moeda}")

    def __add__(self, other: Money) -> Money:
        self._check_moeda(other)
        return Money(centavos=self.centavos + other.centavos, moeda=self.moeda)

    def __sub__(self, other: Money) -> Money:
        self._check_moeda(other)
        return Money(centavos=self.centavos - other.centavos, moeda=self.moeda)

    def __lt__(self, other: Money) -> bool:
        self._check_moeda(other)
        return self.centavos < other.centavos

    def __str__(self) -> str:
        return self.formatado

    def __repr__(self) -> str:
        return f"Money({self.centavos}, '{self.moeda}')"
