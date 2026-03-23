from enum import Enum


class CobrancaTipo(Enum):
    """Tipo de ação de cobrança."""

    LEMBRETE = "lembrete"
    COBRANCA = "cobranca"
    FOLLOW_UP = "follow_up"
    ESCALACAO = "escalacao"


class CobrancaCanal(Enum):
    """Canal de envio da cobrança."""

    WHATSAPP = "whatsapp"
    EMAIL = "email"
    SMS = "sms"


class CobrancaTom(Enum):
    """Tom da mensagem de cobrança, com intensidade progressiva."""

    AMIGAVEL = "amigavel"
    NEUTRO = "neutro"
    FIRME = "firme"
    URGENTE = "urgente"

    @property
    def intensidade(self) -> int:
        """Intensidade numérica para comparação e ordenação."""
        ordem = {"amigavel": 1, "neutro": 2, "firme": 3, "urgente": 4}
        return ordem[self.value]


class CobrancaStatus(Enum):
    """Status de entrega de uma cobrança."""

    ENVIADO = "enviado"
    ENTREGUE = "entregue"
    LIDO = "lido"
    RESPONDIDO = "respondido"
    PAUSADO = "pausado"
