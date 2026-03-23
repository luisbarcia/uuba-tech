"""Value Object para CPF e CNPJ com validação real de dígitos verificadores.

Aceita entrada com ou sem pontuação, armazena apenas dígitos,
e valida usando o algoritmo oficial de dígitos verificadores.

Example:
    >>> doc = Documento("529.982.247-25")
    >>> doc.valor
    '52998224725'
    >>> doc.tipo
    'cpf'
    >>> doc.formatado
    '529.982.247-25'
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal


def _validar_cpf(digitos: str) -> bool:
    """Valida CPF usando algoritmo dos dígitos verificadores.

    Args:
        digitos: String com exatamente 11 dígitos numéricos.

    Returns:
        True se o CPF é válido, False caso contrário.
        Rejeita CPFs com todos os dígitos iguais (ex: 00000000000).
    """
    if len(digitos) != 11 or len(set(digitos)) == 1:
        return False
    for i in range(9, 11):
        soma = sum(int(digitos[j]) * ((i + 1) - j) for j in range(i))
        resto = (soma * 10) % 11
        if resto == 10:
            resto = 0
        if resto != int(digitos[i]):
            return False
    return True


def _validar_cnpj(digitos: str) -> bool:
    """Valida CNPJ usando algoritmo dos dígitos verificadores.

    Args:
        digitos: String com exatamente 14 dígitos numéricos.

    Returns:
        True se o CNPJ é válido, False caso contrário.
        Rejeita CNPJs com todos os dígitos iguais.
    """
    if len(digitos) != 14 or len(set(digitos)) == 1:
        return False
    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(int(digitos[i]) * pesos1[i] for i in range(12))
    resto = soma % 11
    d1 = 0 if resto < 2 else 11 - resto
    if int(digitos[12]) != d1:
        return False
    soma = sum(int(digitos[i]) * pesos2[i] for i in range(13))
    resto = soma % 11
    d2 = 0 if resto < 2 else 11 - resto
    return int(digitos[13]) == d2


@dataclass(frozen=True)
class Documento:
    """Value Object imutável para CPF ou CNPJ.

    Aceita entrada com ou sem pontuação (pontos, traços, barras são removidos).
    Armazena internamente apenas os dígitos. Valida dígitos verificadores reais
    — ``Documento("00000000000")`` levanta ``ValueError``.

    Attributes:
        valor: Dígitos do documento (11 para CPF, 14 para CNPJ).

    Raises:
        ValueError: Se o documento tem tamanho inválido ou falha na validação.

    Example:
        >>> cpf = Documento("52998224725")
        >>> cpf.tipo
        'cpf'
        >>> cpf.formatado
        '529.982.247-25'
        >>> cnpj = Documento("11.222.333/0001-81")
        >>> cnpj.valor
        '11222333000181'
    """

    valor: str

    def __init__(self, raw: str) -> None:
        """Cria um Documento a partir de uma string com ou sem pontuação.

        Args:
            raw: CPF ou CNPJ, com ou sem formatação.
                 Ex: ``"52998224725"``, ``"529.982.247-25"``,
                 ``"11222333000181"``, ``"11.222.333/0001-81"``.

        Raises:
            ValueError: Se o número de dígitos não é 11 (CPF) nem 14 (CNPJ),
                        ou se os dígitos verificadores são inválidos.
        """
        digitos = re.sub(r"\D", "", raw)
        if len(digitos) == 11:
            if not _validar_cpf(digitos):
                raise ValueError(f"CPF inválido: {raw}")
        elif len(digitos) == 14:
            if not _validar_cnpj(digitos):
                raise ValueError(f"CNPJ inválido: {raw}")
        else:
            raise ValueError(f"Documento deve ter 11 ou 14 dígitos, recebeu {len(digitos)}: {raw}")
        object.__setattr__(self, "valor", digitos)

    @property
    def tipo(self) -> Literal["cpf", "cnpj"]:
        """Tipo do documento: ``"cpf"`` (11 dígitos) ou ``"cnpj"`` (14 dígitos)."""
        return "cpf" if len(self.valor) == 11 else "cnpj"

    @property
    def formatado(self) -> str:
        """Documento com pontuação padrão.

        Returns:
            CPF: ``"529.982.247-25"``
            CNPJ: ``"11.222.333/0001-81"``
        """
        if self.tipo == "cpf":
            return f"{self.valor[:3]}.{self.valor[3:6]}.{self.valor[6:9]}-{self.valor[9:]}"
        return f"{self.valor[:2]}.{self.valor[2:5]}.{self.valor[5:8]}/{self.valor[8:12]}-{self.valor[12:]}"

    def __str__(self) -> str:
        return self.valor

    def __repr__(self) -> str:
        return f"Documento('{self.valor}')"
