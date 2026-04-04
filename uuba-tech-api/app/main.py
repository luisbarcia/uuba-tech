import logging
import json as json_lib

from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse
from scalar_fastapi import get_scalar_api_reference
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.types import ASGIApp, Message, Receive, Scope, Send
from app.utils.ids import generate_id
from app.exceptions import APIError
from app.database import get_db


# --- Structured logging ---
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "msg": record.getMessage(),
            "module": record.module,
        }
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        return json_lib.dumps(log_data, ensure_ascii=False)


handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logging.basicConfig(level=logging.INFO, handlers=[handler], force=True)
logger = logging.getLogger("uuba")


# --- App ---
API_DESCRIPTION = """
# Uúba Tech API

API de cobrança inteligente para PMEs brasileiras.

## Getting Started

### Autenticação

Todas as requisições exigem uma API Key no header:

```
X-API-Key: sua_chave_aqui
```

### Base URL

```
https://api.uuba.tech
```

### Primeira requisição

Crie um cliente:

```bash
curl -X POST https://api.uuba.tech/api/v1/clientes \\
  -H "X-API-Key: sua_chave_aqui" \\
  -H "Content-Type: application/json" \\
  -d '{
    "nome": "Padaria Bom Pão",
    "documento": "12345678000190",
    "telefone": "5511999001234"
  }'
```

Resposta:

```json
{
  "id": "cli_abc123def456",
  "object": "cliente",
  "nome": "Padaria Bom Pão",
  "documento": "12345678000190",
  "telefone": "5511999001234",
  "created_at": "2026-03-15T10:00:00-03:00",
  "updated_at": "2026-03-15T10:00:00-03:00"
}
```

### Criar uma fatura

```bash
curl -X POST https://api.uuba.tech/api/v1/faturas \\
  -H "X-API-Key: sua_chave_aqui" \\
  -H "Content-Type: application/json" \\
  -d '{
    "cliente_id": "cli_abc123def456",
    "valor": 250000,
    "vencimento": "2026-04-01T00:00:00-03:00",
    "descricao": "NF 1234 - Serviços março"
  }'
```

> **Nota:** Valores monetários são sempre em **centavos**. R$ 2.500,00 = `250000`.

### Consultar métricas do cliente

```bash
curl https://api.uuba.tech/api/v1/clientes/cli_abc123def456/metricas \\
  -H "X-API-Key: sua_chave_aqui"
```

Resposta:

```json
{
  "dso_dias": 28.5,
  "total_em_aberto": 430000,
  "total_vencido": 120000,
  "faturas_em_aberto": 3,
  "faturas_vencidas": 1
}
```

## Convenções

| Convenção | Detalhe |
|-----------|---------|
| **IDs** | Prefixo descritivo + nanoid: `cli_`, `fat_`, `cob_` |
| **Valores** | Inteiro em centavos. `15000` = R$ 150,00 |
| **Datas** | ISO 8601 com timezone: `2026-03-15T10:00:00-03:00` |
| **Status** | Strings descritivas: `pendente`, `pago`, `vencido`, `cancelado` |
| **Campos** | snake_case em todo lugar |

## Erros

A API usa [RFC 9457 (Problem Details)](https://www.rfc-editor.org/rfc/rfc9457) para todas as respostas de erro:

```json
{
  "type": "https://api.uubatech.com/errors/fatura-nao-encontrada",
  "title": "Fatura não encontrada",
  "status": 404,
  "detail": "Fatura fat_abc123 não existe.",
  "instance": "/api/v1/faturas/fat_abc123",
  "request_id": "req_7f3a2b1c4d5e",
  "errors": []
}
```

| Status | Significado |
|--------|-------------|
| `401` | API Key ausente ou inválida |
| `404` | Recurso não encontrado |
| `409` | Conflito de integridade (FK ou UNIQUE violation) |
| `422` | Erro de validação nos dados enviados |
| `500` | Erro interno do servidor |

## Paginação

Endpoints de listagem retornam envelope paginado:

```json
{
  "object": "list",
  "data": [...],
  "pagination": {
    "total": 42,
    "page_size": 50,
    "has_more": false,
    "offset": 0
  }
}
```

Parâmetros: `?limit=50&offset=0`

## Rate Limiting

Por enquanto sem limite. Quando implementado, os headers padrão serão:

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1709994000
```
"""

app = FastAPI(
    title="Uúba Tech API",
    version="0.1.0",
    description=API_DESCRIPTION,
    contact={"name": "Uúba Tech", "url": "https://uuba.tech"},
    openapi_tags=[
        {
            "name": "clientes",
            "description": "Gerencie os clientes da sua carteira de recebíveis. Cada cliente é identificado por CPF ou CNPJ (único) e pode ter um número de WhatsApp associado para comunicação automática. Use o endpoint de métricas para acompanhar o comportamento de pagamento (DSO, aging, histórico).",
        },
        {
            "name": "faturas",
            "description": "Registre e acompanhe faturas a receber. Valores são sempre em centavos (`250000` = R$ 2.500,00). Uma fatura passa pelos status `pendente` → `vencido` → `pago` ou `cancelado`. Use filtros por status e cliente para consultar a carteira.",
        },
        {
            "name": "cobrancas",
            "description": "Acompanhe as ações de cobrança realizadas sobre cada fatura. Cada cobrança registra o canal (WhatsApp, email), o tom da mensagem (amigável, neutro, firme, urgente), e pode ser pausada ou retomada. Use o histórico por fatura para ver toda a timeline de comunicação com o cliente.",
        },
        {
            "name": "jobs",
            "description": "Jobs agendáveis (cron) para operações em lote. Idempotentes — seguros para executar múltiplas vezes. Requerem autenticação.",
        },
        {
            "name": "admin",
            "description": "Endpoints administrativos para seed de dados mock, reset do banco e operações de manutenção. Requerem autenticação.",
        },
        {
            "name": "tenants",
            "description": "Gerenciamento de tenants (multi-tenancy). Cada tenant eh uma empresa cliente da UUBA com seus proprios clientes, faturas e reguas de cobranca.",
        },
        {
            "name": "metricas",
            "description": "Metricas agregadas da plataforma: DSO, revenue, overdue, clientes ativos/inativos. Filtro opcional por tenant.",
        },
        {
            "name": "infraestrutura",
            "description": "Endpoints de monitoramento e operacao. Nao requerem autenticacao.",
        },
    ],
    docs_url=None,
    redoc_url=None,
)


# --- Scalar API Docs ---
@app.get("/docs", include_in_schema=False)
async def scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title,
    )


# --- Exception handlers ---
@app.exception_handler(APIError)
async def api_error_handler(request: Request, exc: APIError):
    return JSONResponse(
        status_code=exc.status,
        content={
            "type": f"https://api.uubatech.com/errors/{exc.error_type}",
            "title": exc.title,
            "status": exc.status,
            "detail": exc.detail,
            "instance": str(request.url.path),
            "request_id": getattr(request.state, "request_id", ""),
            "errors": [],
        },
    )


@app.exception_handler(Exception)
async def generic_error_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error")
    from sqlalchemy.exc import IntegrityError

    if isinstance(exc, IntegrityError):
        return JSONResponse(
            status_code=409,
            content={
                "type": "https://api.uubatech.com/errors/integridade",
                "title": "Erro de integridade",
                "status": 409,
                "detail": "Violação de integridade de dados. Verifique os dados enviados.",
                "instance": str(request.url.path),
                "request_id": getattr(request.state, "request_id", ""),
                "errors": [],
            },
        )
    return JSONResponse(
        status_code=500,
        content={
            "type": "https://api.uubatech.com/errors/interno",
            "title": "Erro interno",
            "status": 500,
            "detail": "Erro inesperado no servidor",
            "instance": str(request.url.path),
            "request_id": getattr(request.state, "request_id", ""),
            "errors": [],
        },
    )


# --- Middleware (pure ASGI — não interfere com exception handlers) ---
class RequestIdMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_id = generate_id("req")
        scope.setdefault("state", {})["request_id"] = request_id
        logger.info(
            f"{scope.get('method', '')} {scope.get('path', '')}",
            extra={"request_id": request_id},
        )

        async def send_with_request_id(message: Message):
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                headers.append((b"x-request-id", request_id.encode()))
                message["headers"] = headers
            await send(message)

        await self.app(scope, receive, send_with_request_id)


app.add_middleware(RequestIdMiddleware)

from app.middleware.rate_limit import RateLimitMiddleware  # noqa: E402

app.add_middleware(RateLimitMiddleware)


# --- Routers ---
from app.routers import (  # noqa: E402
    clientes,
    faturas,
    cobrancas,
    admin,
    jobs,
    import_csv,
    privacidade,
    tenants,
    metricas,
    watch,
    logs,
    usage,
    webhooks,
    v0_faturas,
)

app.include_router(v0_faturas.router)
app.include_router(clientes.router)
app.include_router(faturas.router)
app.include_router(cobrancas.router)
app.include_router(admin.router)
app.include_router(jobs.router)
app.include_router(import_csv.router)
app.include_router(privacidade.router)
app.include_router(tenants.router)
app.include_router(metricas.router)
app.include_router(watch.router)
app.include_router(logs.router)
app.include_router(usage.router)
app.include_router(webhooks.router)


# --- Health ---
@app.get(
    "/health",
    tags=["infraestrutura"],
    summary="Verificar saúde da API",
    description="Verifica se a API está respondendo e se a conexão com o banco de dados está ativa. Use para monitoramento e health checks.",
)
async def health(db: AsyncSession = Depends(get_db)):
    await db.execute(text("SELECT 1"))
    return {"status": "ok", "version": app.version}
