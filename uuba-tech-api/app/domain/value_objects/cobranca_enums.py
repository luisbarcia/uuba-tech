"""Enums tipados para cobrança, substituindo strings mágicas.

Define tipo, canal, tom e status de cobrança como enums Python,
eliminando Primitive Obsession e centralizando valores válidos.

Example:
    >>> CobrancaTom.AMIGAVEL.intensidade
    1
    >>> CobrancaTom.URGENTE.intensidade
    4
"""

from enum import Enum


class CobrancaTipo(Enum):
    """Tipo de ação de cobrança.

    Attributes:
        LEMBRETE: Lembrete amigável pré-vencimento ou pós-vencimento leve.
        COBRANCA: Cobrança formal.
        FOLLOW_UP: Follow-up após promessa de pagamento ou sem resposta.
        ESCALACAO: Escalação para atendente humano ou ação mais firme.
    """

    LEMBRETE = "lembrete"
    COBRANCA = "cobranca"
    FOLLOW_UP = "follow_up"
    ESCALACAO = "escalacao"


class CobrancaCanal(Enum):
    """Canal de envio da cobrança.

    Attributes:
        WHATSAPP: Via Evolution API (self-hosted).
        EMAIL: Via SMTP ou serviço de email.
        SMS: Via provedor SMS (futuro).
    """

    WHATSAPP = "whatsapp"
    EMAIL = "email"
    SMS = "sms"


class CobrancaTom(Enum):
    """Tom da mensagem de cobrança, com intensidade progressiva.

    A régua de cobrança usa a ``intensidade`` para escalar o tom
    automaticamente ao longo dos dias de atraso.

    Attributes:
        AMIGAVEL: Tom leve, usado em lembretes (intensidade 1).
        NEUTRO: Tom neutro, usado em primeiras cobranças (intensidade 2).
        FIRME: Tom assertivo, usado após sem resposta (intensidade 3).
        URGENTE: Tom de urgência, usado antes de escalação (intensidade 4).

    Example:
        >>> CobrancaTom.AMIGAVEL.intensidade < CobrancaTom.URGENTE.intensidade
        True
    """

    AMIGAVEL = "amigavel"
    NEUTRO = "neutro"
    FIRME = "firme"
    URGENTE = "urgente"

    @property
    def intensidade(self) -> int:
        """Intensidade numérica (1-4) para comparação e ordenação.

        Returns:
            1 (amigável) a 4 (urgente).
        """
        ordem = {"amigavel": 1, "neutro": 2, "firme": 3, "urgente": 4}
        return ordem[self.value]


class CobrancaStatus(Enum):
    """Status de entrega de uma cobrança.

    Attributes:
        ENVIADO: Mensagem enviada ao provedor (WhatsApp/Email/SMS).
        ENTREGUE: Confirmação de entrega pelo provedor.
        LIDO: Mensagem lida pelo destinatário (quando disponível).
        RESPONDIDO: Destinatário respondeu à mensagem.
        PAUSADO: Cobrança pausada manualmente ou por regra de compliance.
    """

    ENVIADO = "enviado"
    ENTREGUE = "entregue"
    LIDO = "lido"
    RESPONDIDO = "respondido"
    PAUSADO = "pausado"
