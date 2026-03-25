"""Endpoint público de privacidade (LGPD Art. 9).

Sem autenticação — acessível a qualquer titular de dados.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1", tags=["lgpd"])

_AVISO = {
    "versao": "1.0",
    "atualizado_em": "2026-03-25",
    "controlador": {
        "nome": "UÚBA Tecnologia Ltda.",
        "contato_lgpd": "privacidade@uuba.tech",
    },
    "dados_coletados": [
        {
            "dado": "Nome completo ou razão social",
            "finalidade": "Identificação do titular da dívida",
            "base_legal": "Execução de contrato (Art. 7, V)",
        },
        {
            "dado": "CPF ou CNPJ",
            "finalidade": "Identificação única e validação cadastral",
            "base_legal": "Execução de contrato (Art. 7, V)",
        },
        {
            "dado": "Email",
            "finalidade": "Canal de comunicação para cobrança",
            "base_legal": "Exercício regular de direitos (Art. 7, VI)",
        },
        {
            "dado": "Telefone/WhatsApp",
            "finalidade": "Canal de comunicação para cobrança",
            "base_legal": "Exercício regular de direitos (Art. 7, VI)",
        },
        {
            "dado": "Dados de faturas (valor, vencimento, status)",
            "finalidade": "Registro de obrigação financeira",
            "base_legal": "Obrigação legal (Art. 7, II)",
        },
    ],
    "retencao": {
        "cadastro_cliente": "Relação comercial + 5 anos",
        "faturas": "5 anos após resolução",
        "mensagens_cobranca": "2 anos após resolução da fatura",
        "clientes_inativos": "Anonimizados após 5 anos de inatividade",
    },
    "direitos_titular": [
        "Acesso a todos os dados pessoais armazenados",
        "Correção de dados incompletos ou inexatos",
        "Eliminação de dados pessoais",
        "Portabilidade em formato estruturado (JSON)",
        "Informações sobre compartilhamento de dados",
    ],
    "como_exercer_direitos": {
        "email": "privacidade@uuba.tech",
        "prazo_resposta": "15 dias corridos (Art. 19)",
    },
    "compartilhamento": [
        "Conta Azul (geração de links de pagamento)",
        "WhatsApp Business API (envio de mensagens)",
    ],
    "anpd": "https://www.gov.br/anpd",
}


@router.get(
    "/privacidade",
    summary="Aviso de privacidade (LGPD)",
    description="Retorna o aviso de privacidade conforme Art. 9 da LGPD. "
    "Endpoint público — não requer autenticação.",
)
async def get_aviso_privacidade():
    return _AVISO
