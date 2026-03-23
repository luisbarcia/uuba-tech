"""Value Object para valores monetários em centavos.

Encapsula valor + moeda como unidade atômica. Todas as operações retornam
novos objetos Money (imutável). Impede operações entre moedas diferentes.

Example:
    >>> total = Money(250000)
    >>> total.formatado
    'R$ 2.500,00'
    >>> total - Money(50000)
    Money(200000, 'BRL')
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from functools import total_ordering


@total_ordering
@dataclass(frozen=True)
class Money:
    """Valor monetário imutável em centavos com moeda.

    Usa centavos (int) internamente para evitar erros de ponto flutuante.
    Suporta adição, subtração e comparação entre valores da mesma moeda.

    Attributes:
        centavos: Valor em centavos (>= 0). Ex: 250000 = R$ 2.500,00.
        moeda: Código ISO 4217 da moeda. Default: ``"BRL"``.

    Raises:
        ValueError: Se centavos < 0 na criação.

    Example:
        >>> fatura = Money(150000)  # R$ 1.500,00
        >>> pagamento = Money(50000)  # R$ 500,00
        >>> restante = fatura - pagamento
        >>> restante.formatado
        'R$ 1.000,00'
        >>> restante.reais
        Decimal('1000.00')
    """

    centavos: int
    moeda: str = "BRL"

    def __post_init__(self) -> None:
        if self.centavos < 0:
            raise ValueError(f"Valor não pode ser negativo: {self.centavos}")

    @classmethod
    def zero(cls, moeda: str = "BRL") -> Money:
        """Cria um Money com valor zero.

        Args:
            moeda: Código da moeda. Default: ``"BRL"``.

        Returns:
            Money com centavos=0.
        """
        return cls(centavos=0, moeda=moeda)

    @property
    def reais(self) -> Decimal:
        """Valor convertido para reais como Decimal (precisão exata).

        Example:
            >>> Money(25050).reais
            Decimal('250.50')
        """
        return Decimal(self.centavos) / Decimal(100)

    @property
    def is_zero(self) -> bool:
        """True se o valor é zero."""
        return self.centavos == 0

    @property
    def formatado(self) -> str:
        """Valor formatado em Real brasileiro (R$ X.XXX,XX).

        Example:
            >>> Money(250000).formatado
            'R$ 2.500,00'
            >>> Money(99).formatado
            'R$ 0,99'
        """
        reais = self.centavos / 100
        formatado = f"{reais:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"R$ {formatado}"

    def _check_moeda(self, other: Money) -> None:
        """Verifica compatibilidade de moeda antes de operação.

        Raises:
            ValueError: Se as moedas são diferentes.
        """
        if self.moeda != other.moeda:
            raise ValueError(f"Não é possível operar {self.moeda} com {other.moeda}")

    def __add__(self, other: Money) -> Money:
        """Soma dois Money da mesma moeda. Retorna novo Money.

        Raises:
            ValueError: Se as moedas são diferentes.
        """
        self._check_moeda(other)
        return Money(centavos=self.centavos + other.centavos, moeda=self.moeda)

    def __sub__(self, other: Money) -> Money:
        """Subtrai dois Money da mesma moeda. Retorna novo Money.

        Raises:
            ValueError: Se as moedas são diferentes ou resultado negativo.
        """
        self._check_moeda(other)
        return Money(centavos=self.centavos - other.centavos, moeda=self.moeda)

    def __lt__(self, other: Money) -> bool:
        """Comparação menor-que entre Money da mesma moeda.

        Raises:
            ValueError: Se as moedas são diferentes.
        """
        self._check_moeda(other)
        return self.centavos < other.centavos

    def __str__(self) -> str:
        return self.formatado

    def __repr__(self) -> str:
        return f"Money({self.centavos}, '{self.moeda}')"
