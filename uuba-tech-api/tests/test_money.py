from app.utils.money import centavos_to_reais, reais_to_centavos


def test_centavos_to_reais_basic():
    assert centavos_to_reais(15000) == "R$ 150,00"


def test_centavos_to_reais_zero():
    assert centavos_to_reais(0) == "R$ 0,00"


def test_centavos_to_reais_cents_only():
    assert centavos_to_reais(99) == "R$ 0,99"


def test_centavos_to_reais_large():
    assert centavos_to_reais(1000000) == "R$ 10.000,00"


def test_centavos_to_reais_one_centavo():
    assert centavos_to_reais(1) == "R$ 0,01"


def test_reais_to_centavos_basic():
    assert reais_to_centavos(150.00) == 15000


def test_reais_to_centavos_zero():
    assert reais_to_centavos(0) == 0


def test_reais_to_centavos_rounding():
    assert reais_to_centavos(10.999) == 1100


def test_reais_to_centavos_float_precision():
    assert reais_to_centavos(0.1 + 0.2) == 30
