def centavos_to_reais(centavos: int) -> str:
    """15000 → 'R$ 150,00'"""
    reais = centavos / 100
    return f"R$ {reais:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def reais_to_centavos(reais: float) -> int:
    """150.00 → 15000"""
    return int(round(reais * 100))
