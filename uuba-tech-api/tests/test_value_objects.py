"""Testes unitários para Value Objects do domínio (DP-01).

Seguem TDD strict: cada teste foi escrito ANTES da implementação.
"""

import pytest
from decimal import Decimal

# ── Phase 1: FaturaStatus ──────────────────────────────────────────


class TestFaturaStatus:
    """Testa enum FaturaStatus com transições de máquina de estados."""

    def test_valores_existem(self):
        from app.domain.value_objects.fatura_status import FaturaStatus

        assert FaturaStatus.PENDENTE.value == "pendente"
        assert FaturaStatus.VENCIDO.value == "vencido"
        assert FaturaStatus.PAGO.value == "pago"
        assert FaturaStatus.CANCELADO.value == "cancelado"

    def test_criar_de_string(self):
        from app.domain.value_objects.fatura_status import FaturaStatus

        assert FaturaStatus("pendente") == FaturaStatus.PENDENTE
        assert FaturaStatus("pago") == FaturaStatus.PAGO

    def test_criar_de_string_invalida_levanta_erro(self):
        from app.domain.value_objects.fatura_status import FaturaStatus

        with pytest.raises(ValueError):
            FaturaStatus("inexistente")

    def test_pendente_pode_transicionar_para_pago(self):
        from app.domain.value_objects.fatura_status import FaturaStatus

        assert FaturaStatus.PENDENTE.pode_transicionar_para(FaturaStatus.PAGO) is True

    def test_pendente_pode_transicionar_para_vencido(self):
        from app.domain.value_objects.fatura_status import FaturaStatus

        assert FaturaStatus.PENDENTE.pode_transicionar_para(FaturaStatus.VENCIDO) is True

    def test_pendente_pode_transicionar_para_cancelado(self):
        from app.domain.value_objects.fatura_status import FaturaStatus

        assert FaturaStatus.PENDENTE.pode_transicionar_para(FaturaStatus.CANCELADO) is True

    def test_vencido_pode_transicionar_para_pago(self):
        from app.domain.value_objects.fatura_status import FaturaStatus

        assert FaturaStatus.VENCIDO.pode_transicionar_para(FaturaStatus.PAGO) is True

    def test_vencido_pode_transicionar_para_cancelado(self):
        from app.domain.value_objects.fatura_status import FaturaStatus

        assert FaturaStatus.VENCIDO.pode_transicionar_para(FaturaStatus.CANCELADO) is True

    def test_pago_nao_transiciona_para_nada(self):
        from app.domain.value_objects.fatura_status import FaturaStatus

        assert FaturaStatus.PAGO.pode_transicionar_para(FaturaStatus.PENDENTE) is False
        assert FaturaStatus.PAGO.pode_transicionar_para(FaturaStatus.VENCIDO) is False
        assert FaturaStatus.PAGO.pode_transicionar_para(FaturaStatus.CANCELADO) is False

    def test_cancelado_nao_transiciona_para_nada(self):
        from app.domain.value_objects.fatura_status import FaturaStatus

        assert FaturaStatus.CANCELADO.pode_transicionar_para(FaturaStatus.PENDENTE) is False
        assert FaturaStatus.CANCELADO.pode_transicionar_para(FaturaStatus.PAGO) is False

    def test_nao_transiciona_para_si_mesmo(self):
        from app.domain.value_objects.fatura_status import FaturaStatus

        assert FaturaStatus.PENDENTE.pode_transicionar_para(FaturaStatus.PENDENTE) is False

    def test_is_terminal_pago(self):
        from app.domain.value_objects.fatura_status import FaturaStatus

        assert FaturaStatus.PAGO.is_terminal is True

    def test_is_terminal_cancelado(self):
        from app.domain.value_objects.fatura_status import FaturaStatus

        assert FaturaStatus.CANCELADO.is_terminal is True

    def test_is_terminal_pendente(self):
        from app.domain.value_objects.fatura_status import FaturaStatus

        assert FaturaStatus.PENDENTE.is_terminal is False

    def test_is_terminal_vencido(self):
        from app.domain.value_objects.fatura_status import FaturaStatus

        assert FaturaStatus.VENCIDO.is_terminal is False

    def test_transicoes_validas_pendente(self):
        from app.domain.value_objects.fatura_status import FaturaStatus

        validas = FaturaStatus.PENDENTE.transicoes_validas
        assert set(validas) == {FaturaStatus.PAGO, FaturaStatus.VENCIDO, FaturaStatus.CANCELADO}

    def test_transicoes_validas_terminal_eh_vazio(self):
        from app.domain.value_objects.fatura_status import FaturaStatus

        assert FaturaStatus.PAGO.transicoes_validas == []
        assert FaturaStatus.CANCELADO.transicoes_validas == []

    def test_enum_tem_exatamente_4_membros(self):
        """Garante que _TRANSITIONS não contamina os membros do enum."""
        from app.domain.value_objects.fatura_status import FaturaStatus

        membros = list(FaturaStatus)
        assert len(membros) == 4
        assert set(m.value for m in membros) == {"pendente", "vencido", "pago", "cancelado"}


# ── Phase 2: Enums de Cobrança ─────────────────────────────────────


class TestCobrancaEnums:
    """Testa enums de tipo, canal, tom e status de cobrança."""

    def test_cobranca_tipo_valores(self):
        from app.domain.value_objects.cobranca_enums import CobrancaTipo

        assert CobrancaTipo.LEMBRETE.value == "lembrete"
        assert CobrancaTipo.COBRANCA.value == "cobranca"
        assert CobrancaTipo.FOLLOW_UP.value == "follow_up"
        assert CobrancaTipo.ESCALACAO.value == "escalacao"

    def test_cobranca_canal_valores(self):
        from app.domain.value_objects.cobranca_enums import CobrancaCanal

        assert CobrancaCanal.WHATSAPP.value == "whatsapp"
        assert CobrancaCanal.EMAIL.value == "email"
        assert CobrancaCanal.SMS.value == "sms"

    def test_cobranca_tom_valores(self):
        from app.domain.value_objects.cobranca_enums import CobrancaTom

        assert CobrancaTom.AMIGAVEL.value == "amigavel"
        assert CobrancaTom.NEUTRO.value == "neutro"
        assert CobrancaTom.FIRME.value == "firme"
        assert CobrancaTom.URGENTE.value == "urgente"

    def test_cobranca_tom_ordem_progressiva(self):
        from app.domain.value_objects.cobranca_enums import CobrancaTom

        assert CobrancaTom.AMIGAVEL.intensidade < CobrancaTom.NEUTRO.intensidade
        assert CobrancaTom.NEUTRO.intensidade < CobrancaTom.FIRME.intensidade
        assert CobrancaTom.FIRME.intensidade < CobrancaTom.URGENTE.intensidade

    def test_cobranca_status_valores(self):
        from app.domain.value_objects.cobranca_enums import CobrancaStatus

        assert CobrancaStatus.ENVIADO.value == "enviado"
        assert CobrancaStatus.ENTREGUE.value == "entregue"
        assert CobrancaStatus.LIDO.value == "lido"
        assert CobrancaStatus.RESPONDIDO.value == "respondido"
        assert CobrancaStatus.PAUSADO.value == "pausado"

    def test_criar_de_string(self):
        from app.domain.value_objects.cobranca_enums import CobrancaTipo

        assert CobrancaTipo("lembrete") == CobrancaTipo.LEMBRETE

    def test_criar_de_string_invalida(self):
        from app.domain.value_objects.cobranca_enums import CobrancaTipo

        with pytest.raises(ValueError):
            CobrancaTipo("invalido")


# ── Phase 3: Documento (CPF/CNPJ) ──────────────────────────────────


class TestDocumento:
    """Testa Value Object Documento com validação real de CPF/CNPJ."""

    def test_cpf_valido(self):
        from app.domain.value_objects.documento import Documento

        doc = Documento("52998224725")
        assert doc.valor == "52998224725"
        assert doc.tipo == "cpf"

    def test_cnpj_valido(self):
        from app.domain.value_objects.documento import Documento

        doc = Documento("11222333000181")
        assert doc.valor == "11222333000181"
        assert doc.tipo == "cnpj"

    def test_cpf_formatado(self):
        from app.domain.value_objects.documento import Documento

        doc = Documento("52998224725")
        assert doc.formatado == "529.982.247-25"

    def test_cnpj_formatado(self):
        from app.domain.value_objects.documento import Documento

        doc = Documento("11222333000181")
        assert doc.formatado == "11.222.333/0001-81"

    def test_cpf_com_pontuacao_eh_limpo(self):
        from app.domain.value_objects.documento import Documento

        doc = Documento("529.982.247-25")
        assert doc.valor == "52998224725"
        assert doc.tipo == "cpf"

    def test_cnpj_com_pontuacao_eh_limpo(self):
        from app.domain.value_objects.documento import Documento

        doc = Documento("11.222.333/0001-81")
        assert doc.valor == "11222333000181"

    def test_cpf_invalido_levanta_erro(self):
        from app.domain.value_objects.documento import Documento

        with pytest.raises(ValueError, match="CPF inválido"):
            Documento("00000000000")

    def test_cnpj_invalido_levanta_erro(self):
        from app.domain.value_objects.documento import Documento

        with pytest.raises(ValueError, match="CNPJ inválido"):
            Documento("00000000000000")

    def test_tamanho_errado_levanta_erro(self):
        from app.domain.value_objects.documento import Documento

        with pytest.raises(ValueError, match="deve ter 11 ou 14 dígitos"):
            Documento("1234")

    def test_igualdade(self):
        from app.domain.value_objects.documento import Documento

        assert Documento("52998224725") == Documento("529.982.247-25")

    def test_desigualdade(self):
        from app.domain.value_objects.documento import Documento

        assert Documento("52998224725") != Documento("11222333000181")

    def test_imutavel(self):
        from app.domain.value_objects.documento import Documento

        doc = Documento("52998224725")
        with pytest.raises(AttributeError):
            doc.valor = "outro"

    def test_hashable(self):
        from app.domain.value_objects.documento import Documento

        doc1 = Documento("52998224725")
        doc2 = Documento("52998224725")
        assert hash(doc1) == hash(doc2)
        assert len({doc1, doc2}) == 1

    def test_str(self):
        from app.domain.value_objects.documento import Documento

        doc = Documento("52998224725")
        assert str(doc) == "52998224725"

    def test_cpf_com_espacos_eh_limpo(self):
        from app.domain.value_objects.documento import Documento

        doc = Documento("529 982 247 25")
        assert doc.valor == "52998224725"
        assert doc.tipo == "cpf"

    def test_cnpj_com_digitos_repetidos_levanta_erro(self):
        from app.domain.value_objects.documento import Documento

        with pytest.raises(ValueError, match="CNPJ inválido"):
            Documento("11111111111111")

    def test_documento_vazio_levanta_erro(self):
        from app.domain.value_objects.documento import Documento

        with pytest.raises(ValueError, match="deve ter 11 ou 14 dígitos"):
            Documento("")

    def test_documento_com_letras_extrai_digitos(self):
        from app.domain.value_objects.documento import Documento

        doc = Documento("CPF: 529.982.247-25")
        assert doc.valor == "52998224725"


# ── Phase 4: Money ──────────────────────────────────────────────────


class TestMoney:
    """Testa Value Object Money (valor em centavos + moeda)."""

    def test_criar_money(self):
        from app.domain.value_objects.money import Money

        m = Money(25000)
        assert m.centavos == 25000
        assert m.moeda == "BRL"

    def test_criar_money_com_moeda(self):
        from app.domain.value_objects.money import Money

        m = Money(1000, "USD")
        assert m.moeda == "USD"

    def test_reais(self):
        from app.domain.value_objects.money import Money

        m = Money(25050)
        assert m.reais == Decimal("250.50")

    def test_reais_exato(self):
        from app.domain.value_objects.money import Money

        m = Money(1)
        assert m.reais == Decimal("0.01")

    def test_formatado_brl(self):
        from app.domain.value_objects.money import Money

        m = Money(250000)
        assert m.formatado == "R$ 2.500,00"

    def test_formatado_centavos(self):
        from app.domain.value_objects.money import Money

        m = Money(99)
        assert m.formatado == "R$ 0,99"

    def test_soma(self):
        from app.domain.value_objects.money import Money

        m1 = Money(10000)
        m2 = Money(5000)
        resultado = m1 + m2
        assert resultado.centavos == 15000
        assert resultado.moeda == "BRL"

    def test_subtracao(self):
        from app.domain.value_objects.money import Money

        m1 = Money(10000)
        m2 = Money(3000)
        resultado = m1 - m2
        assert resultado.centavos == 7000

    def test_soma_moedas_diferentes_levanta_erro(self):
        from app.domain.value_objects.money import Money

        with pytest.raises(ValueError, match="Não é possível operar"):
            Money(100, "BRL") + Money(100, "USD")

    def test_valor_negativo_levanta_erro(self):
        from app.domain.value_objects.money import Money

        with pytest.raises(ValueError, match="não pode ser negativo"):
            Money(-100)

    def test_igualdade(self):
        from app.domain.value_objects.money import Money

        assert Money(1000) == Money(1000)
        assert Money(1000, "BRL") == Money(1000, "BRL")

    def test_desigualdade_valor(self):
        from app.domain.value_objects.money import Money

        assert Money(1000) != Money(2000)

    def test_desigualdade_moeda(self):
        from app.domain.value_objects.money import Money

        assert Money(1000, "BRL") != Money(1000, "USD")

    def test_imutavel(self):
        from app.domain.value_objects.money import Money

        m = Money(1000)
        with pytest.raises(AttributeError):
            m.centavos = 2000

    def test_hashable(self):
        from app.domain.value_objects.money import Money

        m1 = Money(1000)
        m2 = Money(1000)
        assert hash(m1) == hash(m2)
        assert len({m1, m2}) == 1

    def test_zero(self):
        from app.domain.value_objects.money import Money

        m = Money.zero()
        assert m.centavos == 0
        assert m.moeda == "BRL"

    def test_is_zero(self):
        from app.domain.value_objects.money import Money

        assert Money.zero().is_zero is True
        assert Money(100).is_zero is False

    def test_comparacao_maior(self):
        from app.domain.value_objects.money import Money

        assert Money(2000) > Money(1000)

    def test_comparacao_menor(self):
        from app.domain.value_objects.money import Money

        assert Money(500) < Money(1000)

    def test_subtracao_negativa_levanta_erro(self):
        from app.domain.value_objects.money import Money

        with pytest.raises(ValueError, match="não pode ser negativo"):
            Money(5000) - Money(10000)

    def test_comparacao_moedas_diferentes_levanta_erro(self):
        from app.domain.value_objects.money import Money

        with pytest.raises(ValueError, match="Não é possível operar"):
            Money(100, "BRL") > Money(100, "USD")

    def test_str(self):
        from app.domain.value_objects.money import Money

        assert str(Money(250000)) == "R$ 2.500,00"
