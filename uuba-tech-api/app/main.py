import logging
import json as json_lib

from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse
from scalar_fastapi import get_scalar_api_reference
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
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
            "description": "Cadastro e métricas de clientes (devedores). Cada cliente tem um documento (CPF/CNPJ) único e pode ter múltiplas faturas.",
        },
        {
            "name": "faturas",
            "description": "CRUD de faturas a receber. Valores em centavos (R$ 150,00 = `15000`). Status: `pendente`, `pago`, `vencido`, `cancelado`.",
        },
        {
            "name": "cobrancas",
            "description": "Registro de cobranças enviadas aos clientes. Cada cobrança está vinculada a uma fatura. Suporte a pausar/retomar régua.",
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
                "detail": str(exc.orig) if exc.orig else "Constraint violation",
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


# --- Middleware ---
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = generate_id("req")
    request.state.request_id = request_id
    logger.info(f"{request.method} {request.url.path}", extra={"request_id": request_id})
    response = await call_next(request)
    response.headers["X-Request-Id"] = request_id
    return response


# --- Routers ---
from app.routers import clientes, faturas, cobrancas
app.include_router(clientes.router)
app.include_router(faturas.router)
app.include_router(cobrancas.router)


# --- Health ---
@app.get("/health")
async def health(db: AsyncSession = Depends(get_db)):
    await db.execute(text("SELECT 1"))
    return {"status": "ok"}
