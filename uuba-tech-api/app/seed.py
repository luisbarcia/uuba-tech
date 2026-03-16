"""Seed de dados mock realistas para demo e testes."""

from datetime import datetime, timezone, timedelta
from app.utils.ids import generate_id

# --- Clientes PMEs brasileiras realistas ---
CLIENTES = [
    {
        "nome": "Padaria Bom Pão Ltda",
        "documento": "12345678000190",
        "email": "financeiro@padariabompao.com.br",
        "telefone": "5511999001234",
    },
    {
        "nome": "Auto Peças Silva ME",
        "documento": "98765432000155",
        "email": "silva@autopecassilva.com.br",
        "telefone": "5511988776655",
    },
    {
        "nome": "Restaurante Sabor da Terra",
        "documento": "45678912000133",
        "email": "contato@sabordaterra.com.br",
        "telefone": "5521977665544",
    },
    {
        "nome": "Construtora Horizonte EIRELI",
        "documento": "78912345000177",
        "email": "ap@construtorah.com.br",
        "telefone": "5531966554433",
    },
    {
        "nome": "Clínica Saúde & Vida",
        "documento": "32165498000122",
        "email": "financeiro@clinicasaudevida.com.br",
        "telefone": "5511955443322",
    },
    {
        "nome": "Tech Solutions Informática",
        "documento": "65498732000188",
        "email": "nf@techsolutions.io",
        "telefone": "5511944332211",
    },
    {
        "nome": "Mercadinho do Zé",
        "documento": "11223344000166",
        "email": None,
        "telefone": "5521933221100",
    },
    {
        "nome": "Escritório Advocacia Mendes",
        "documento": "99887766000144",
        "email": "financeiro@mendesadv.com.br",
        "telefone": "5511922110099",
    },
]


def _date(days_offset: int) -> datetime:
    return datetime.now(timezone.utc) + timedelta(days=days_offset)


def build_seed_data() -> dict:
    """Gera IDs e monta os dados completos para seed."""
    now = datetime.now(timezone.utc)
    clientes = []
    faturas = []
    cobrancas = []

    for c in CLIENTES:
        cli_id = generate_id("cli")
        clientes.append({"id": cli_id, **c, "created_at": now, "updated_at": now})

    # --- Faturas variadas por cliente ---
    cenarios_faturas = [
        # (indice_cliente, valor_centavos, status, dias_vencimento, descricao)
        (0, 350000, "pendente", 15, "NF 1001 - Fornecimento de farinha março"),
        (0, 120000, "vencido", -10, "NF 0987 - Fornecimento de farinha fevereiro"),
        (0, 280000, "pago", -45, "NF 0950 - Fornecimento de farinha janeiro"),
        (1, 890000, "pendente", 20, "NF 2050 - Peças motor diesel lote 42"),
        (1, 450000, "vencido", -5, "NF 2031 - Filtros e correias março"),
        (2, 175000, "pendente", 30, "NF 3100 - Serviço de buffet evento corporativo"),
        (2, 95000, "pago", -30, "NF 3080 - Marmitas fevereiro"),
        (3, 4500000, "vencido", -20, "NF 4500 - Etapa 3 obra residencial Vila Nova"),
        (3, 2800000, "pendente", 10, "NF 4520 - Etapa 4 obra residencial Vila Nova"),
        (4, 320000, "pendente", 25, "NF 5200 - Equipamentos consultório odonto"),
        (4, 150000, "pago", -60, "NF 5150 - Materiais descartáveis janeiro"),
        (5, 780000, "vencido", -15, "NF 6300 - Licenças software anuais"),
        (5, 230000, "pendente", 5, "NF 6320 - Suporte técnico março"),
        (6, 45000, "vencido", -30, "NF 7001 - Produtos de limpeza"),
        (6, 38000, "vencido", -15, "NF 7010 - Bebidas e laticínios"),
        (7, 1200000, "pendente", 45, "NF 8100 - Honorários advocatícios processo X"),
    ]

    for cli_idx, valor, status, dias_venc, desc in cenarios_faturas:
        fat_id = generate_id("fat")
        pago_em = _date(dias_venc + 5) if status == "pago" else None
        faturas.append(
            {
                "id": fat_id,
                "cliente_id": clientes[cli_idx]["id"],
                "valor": valor,
                "moeda": "BRL",
                "status": status,
                "vencimento": _date(dias_venc),
                "descricao": desc,
                "numero_nf": desc.split(" - ")[0].replace("NF ", ""),
                "pago_em": pago_em,
                "created_at": _date(dias_venc - 30),
                "updated_at": now,
            }
        )

    # --- Cobranças para faturas vencidas ---
    mensagens = {
        "lembrete": {
            "amigavel": "Olá! Passando para lembrar da fatura {nf} no valor de R$ {valor}. Qualquer dúvida, estamos à disposição! 😊",
            "neutro": "Prezado(a), informamos que a fatura {nf} no valor de R$ {valor} encontra-se pendente. Favor verificar.",
        },
        "cobranca": {
            "neutro": "Prezado(a), a fatura {nf} no valor de R$ {valor} venceu em {venc}. Solicitamos a regularização.",
            "firme": "Informamos que a fatura {nf} (R$ {valor}) está vencida desde {venc}. É necessário regularizar para evitar restrições.",
        },
        "follow_up": {
            "firme": "Reiteramos que a fatura {nf} (R$ {valor}) permanece em aberto desde {venc}. Favor providenciar o pagamento.",
        },
        "escalacao": {
            "urgente": "URGENTE: A fatura {nf} (R$ {valor}) está em atraso há {dias} dias. Caso não regularizada em 48h, medidas cabíveis serão tomadas.",
        },
    }

    for fat in faturas:
        if fat["status"] != "vencido":
            continue

        cli_id = fat["cliente_id"]
        dias_atraso = (now - fat["vencimento"]).days
        valor_fmt = (
            f"{fat['valor'] / 100:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )
        nf = fat.get("numero_nf", "")
        venc_fmt = fat["vencimento"].strftime("%d/%m/%Y")

        # Lembrete (enviado antes do vencimento)
        cob_id = generate_id("cob")
        cobrancas.append(
            {
                "id": cob_id,
                "fatura_id": fat["id"],
                "cliente_id": cli_id,
                "tipo": "lembrete",
                "canal": "whatsapp",
                "tom": "amigavel",
                "mensagem": mensagens["lembrete"]["amigavel"].format(nf=nf, valor=valor_fmt),
                "status": "entregue",
                "pausado": False,
                "enviado_em": fat["vencimento"] - timedelta(days=3),
                "created_at": fat["vencimento"] - timedelta(days=3),
                "updated_at": now,
            }
        )

        # Cobrança (após vencimento)
        if dias_atraso >= 5:
            cob_id = generate_id("cob")
            cobrancas.append(
                {
                    "id": cob_id,
                    "fatura_id": fat["id"],
                    "cliente_id": cli_id,
                    "tipo": "cobranca",
                    "canal": "whatsapp",
                    "tom": "firme",
                    "mensagem": mensagens["cobranca"]["firme"].format(
                        nf=nf, valor=valor_fmt, venc=venc_fmt
                    ),
                    "status": "lido",
                    "pausado": False,
                    "enviado_em": fat["vencimento"] + timedelta(days=5),
                    "created_at": fat["vencimento"] + timedelta(days=5),
                    "updated_at": now,
                }
            )

        # Follow-up (15+ dias)
        if dias_atraso >= 15:
            cob_id = generate_id("cob")
            cobrancas.append(
                {
                    "id": cob_id,
                    "fatura_id": fat["id"],
                    "cliente_id": cli_id,
                    "tipo": "follow_up",
                    "canal": "whatsapp",
                    "tom": "firme",
                    "mensagem": mensagens["follow_up"]["firme"].format(
                        nf=nf, valor=valor_fmt, venc=venc_fmt
                    ),
                    "status": "enviado",
                    "pausado": False,
                    "enviado_em": fat["vencimento"] + timedelta(days=15),
                    "created_at": fat["vencimento"] + timedelta(days=15),
                    "updated_at": now,
                }
            )

    return {"clientes": clientes, "faturas": faturas, "cobrancas": cobrancas}
