"""Seed da régua padrão UÚBA — protocolo de cobrança progressiva.

D+1: lembrete amigável
D+3: follow-up neutro
D+7: cobrança firme
D+12: cobrança urgente
D+15: última tentativa antes de escalação
"""

from app.utils.ids import generate_id

REGUA_ID = "reg_padrao_uuba"


def build_regua_seed(tenant_id: str) -> dict:
    """Retorna régua padrão com 5 passos progressivos."""
    return {
        "regua": {
            "id": REGUA_ID,
            "tenant_id": tenant_id,
            "nome": "Régua Padrão UÚBA",
            "ativa": True,
        },
        "passos": [
            {
                "id": generate_id("rps"),
                "regua_id": REGUA_ID,
                "ordem": 1,
                "dias_atraso": 1,
                "tipo": "lembrete",
                "canal": "whatsapp",
                "tom": "amigavel",
                "template_mensagem": (
                    "Olá! Passando para lembrar da fatura {numero_nf} no valor de "
                    "R$ {valor}. Venceu em {vencimento}. Segue o link para pagamento: "
                    "{link_pagamento}. Qualquer dúvida, estamos à disposição!"
                ),
            },
            {
                "id": generate_id("rps"),
                "regua_id": REGUA_ID,
                "ordem": 2,
                "dias_atraso": 3,
                "tipo": "follow_up",
                "canal": "whatsapp",
                "tom": "neutro",
                "template_mensagem": (
                    "Boa tarde! Verificamos que a fatura {numero_nf} (R$ {valor}) "
                    "continua em aberto desde {vencimento}. Precisa de ajuda para "
                    "regularizar? Link: {link_pagamento}"
                ),
            },
            {
                "id": generate_id("rps"),
                "regua_id": REGUA_ID,
                "ordem": 3,
                "dias_atraso": 7,
                "tipo": "cobranca",
                "canal": "whatsapp",
                "tom": "firme",
                "template_mensagem": (
                    "Informamos que a fatura {numero_nf} no valor de R$ {valor} está "
                    "vencida há {dias_atraso} dias. É necessário regularizar a situação "
                    "para evitar restrições. Link: {link_pagamento}"
                ),
            },
            {
                "id": generate_id("rps"),
                "regua_id": REGUA_ID,
                "ordem": 4,
                "dias_atraso": 12,
                "tipo": "cobranca",
                "canal": "whatsapp",
                "tom": "urgente",
                "template_mensagem": (
                    "URGENTE: A fatura {numero_nf} (R$ {valor}) está vencida há "
                    "{dias_atraso} dias. Caso não seja regularizada em 3 dias úteis, "
                    "medidas adicionais serão tomadas. Link: {link_pagamento}"
                ),
            },
            {
                "id": generate_id("rps"),
                "regua_id": REGUA_ID,
                "ordem": 5,
                "dias_atraso": 15,
                "tipo": "escalacao",
                "canal": "whatsapp",
                "tom": "urgente",
                "template_mensagem": (
                    "Última tentativa: a fatura {numero_nf} (R$ {valor}, vencida há "
                    "{dias_atraso} dias) será encaminhada para análise de providências "
                    "adicionais. Para resolver agora: {link_pagamento}"
                ),
            },
        ],
    }
