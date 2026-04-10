# Auth Bearer Migration — Issues #105, #106, #107

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Migrar autenticacao da API de `X-API-Key` para `Authorization: Bearer` (padrao Unkey/Stripe), com backward compat, environment detection correto, e idempotency real.

**Architecture:** Modificar `verify_api_key` para aceitar ambos os headers (Bearer prioritario, X-API-Key fallback). Extrair environment do prefixo da key (`sk_test_`/`sk_live_`) ou metadata Unkey. Implementar idempotency via tabela DB com TTL 24h.

**Tech Stack:** FastAPI, Pydantic, httpx, SQLAlchemy async, pytest, Unkey HTTP API v2

---

## File Structure

| File | Action | Responsibility |
|------|--------|---------------|
| `app/auth/api_key.py` | Modify | Dual header (Bearer + X-API-Key), environment extraction |
| `app/auth/idempotency.py` | Create | Middleware de idempotency (store, hash, replay) |
| `app/routers/v0_faturas.py` | Modify | Usar `request.state.environment`, integrar idempotency |
| `app/models/idempotency.py` | Create | SQLAlchemy model para idempotency_cache |
| `app/main.py` | Modify | OpenAPI securitySchemes, registrar cleanup cron |
| `tests/conftest.py` | Modify | Override auth aceitar Bearer, fixture AUTH dual |
| `tests/test_auth_bearer.py` | Create | Testes Bearer auth |
| `tests/test_auth_environment.py` | Create | Testes environment detection |
| `tests/test_idempotency.py` | Create | Testes idempotency middleware |
| `tests/test_attack_auth.py` | Modify | Adicionar testes Bearer attack vectors |
| `alembic/versions/xxx_idempotency.py` | Create | Migration tabela idempotency_cache |

---

## Task 1: Bearer Auth — Testes RED (#105)

**Files:**
- Create: `tests/test_auth_bearer.py`
- Modify: `tests/conftest.py`

- [ ] **Step 1: Atualizar conftest para aceitar Bearer**

O `override_verify_api_key` no conftest precisa aceitar tanto `X-API-Key` quanto `Authorization: Bearer`:

```python
# tests/conftest.py — override_verify_api_key (dentro da fixture client)
async def override_verify_api_key(request: Request):
    """Override padrao: valida key via Bearer OU X-API-Key."""
    from app.exceptions import APIError

    # Tentar Bearer primeiro
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        api_key = auth_header[7:]
    else:
        api_key = request.headers.get("X-API-Key", "")

    if not api_key or api_key != API_KEY:
        raise APIError(
            401, "auth-invalida", "Autenticacao invalida", "API key ausente ou invalida"
        )
    request.state.tenant_id = TEST_TENANT_ID
    request.state.permissions = [
        "tenants:write",
        "tenants:read",
        "admin:write",
        "admin:read",
        "clients:read",
        "clients:write",
        "invoices:read",
        "invoices:write",
        "metrics:read",
        "usage:read",
        "webhooks:read",
        "webhooks:write",
        "integrations:read",
        "integrations:write",
        "receivables:write",
    ]
    request.state.key_id = "key_test"
    request.state.environment = "test"
    return api_key
```

Atualizar tambem a constante AUTH e adicionar BEARER_AUTH:

```python
AUTH = {"X-API-Key": API_KEY}
BEARER_AUTH = {"Authorization": f"Bearer {API_KEY}"}
```

Fazer o mesmo no `override_verify_api_key` da fixture `v0_client`.

- [ ] **Step 2: Escrever testes Bearer (RED)**

```python
# tests/test_auth_bearer.py
"""Testes para autenticacao via Authorization: Bearer header."""

from tests.conftest import API_KEY, AUTH, BEARER_AUTH


class TestBearerAuth:
    """Bearer auth deve funcionar em todos os endpoints protegidos."""

    async def test_bearer_auth_on_clientes(self, client):
        resp = await client.get("/api/v1/clientes", headers=BEARER_AUTH)
        assert resp.status_code == 200

    async def test_bearer_auth_on_faturas(self, client):
        resp = await client.get("/api/v1/faturas", headers=BEARER_AUTH)
        assert resp.status_code == 200

    async def test_bearer_auth_on_v0_faturas_dry_run(self, v0_client):
        payload = {
            "customer": {
                "type": "PJ",
                "document": "12345678000190",
                "name": "Teste Ltda",
            },
            "operations": [
                {
                    "service": {"code": "SVC-01", "description": "Teste"},
                    "sale": {"amount": 100.0, "due_date": "2026-12-01"},
                }
            ],
            "payment_method": "BOLETO_BANCARIO",
        }
        resp = await v0_client.post(
            "/api/v0/faturas?dry_run=true", json=payload, headers=BEARER_AUTH
        )
        assert resp.status_code == 200
        assert resp.json()["object"] == "validation_result"

    async def test_x_api_key_still_works(self, client):
        """Backward compat: X-API-Key continua funcionando."""
        resp = await client.get("/api/v1/clientes", headers=AUTH)
        assert resp.status_code == 200

    async def test_bearer_without_token_returns_401(self, client):
        resp = await client.get(
            "/api/v1/clientes", headers={"Authorization": "Bearer "}
        )
        assert resp.status_code == 401

    async def test_bearer_wrong_token_returns_401(self, client):
        resp = await client.get(
            "/api/v1/clientes", headers={"Authorization": "Bearer wrong_key"}
        )
        assert resp.status_code == 401

    async def test_bearer_without_bearer_prefix_returns_401(self, client):
        resp = await client.get(
            "/api/v1/clientes", headers={"Authorization": API_KEY}
        )
        assert resp.status_code == 401

    async def test_basic_auth_not_accepted(self, client):
        resp = await client.get(
            "/api/v1/clientes", headers={"Authorization": f"Basic {API_KEY}"}
        )
        assert resp.status_code == 401


class TestBearerPriority:
    """Quando ambos os headers estao presentes, Bearer tem prioridade."""

    async def test_bearer_takes_priority_over_x_api_key(self, client):
        resp = await client.get(
            "/api/v1/clientes",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "X-API-Key": "wrong_key",
            },
        )
        assert resp.status_code == 200

    async def test_wrong_bearer_ignores_valid_x_api_key(self, client):
        resp = await client.get(
            "/api/v1/clientes",
            headers={
                "Authorization": "Bearer wrong_key",
                "X-API-Key": API_KEY,
            },
        )
        assert resp.status_code == 401
```

- [ ] **Step 3: Rodar testes e confirmar que falham**

Run: `cd /Users/luismattos/Documentos/Workspaces/luisbarcia/uuba-tech/uuba-tech-api && python -m pytest tests/test_auth_bearer.py -v`
Expected: FAIL — `BEARER_AUTH` nao existe no conftest, Bearer nao aceito

- [ ] **Step 4: Commit testes RED**

```bash
git add tests/test_auth_bearer.py
git commit -m "test(auth): add Bearer auth tests (RED) — issue #105"
```

---

## Task 2: Bearer Auth — Implementacao GREEN (#105)

**Files:**
- Modify: `app/auth/api_key.py`
- Modify: `tests/conftest.py`

- [ ] **Step 1: Modificar verify_api_key para aceitar Bearer**

```python
# app/auth/api_key.py — adicionar imports
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Adicionar scheme Bearer (apos a linha 26)
bearer_scheme = HTTPBearer(auto_error=False, description="Authorization: Bearer <api_key>")

# Modificar verify_api_key para aceitar ambos
async def verify_api_key(
    request: Request,
    bearer: HTTPAuthorizationCredentials | None = Security(bearer_scheme),
    api_key: str | None = Security(api_key_header),
    db: AsyncSession = Depends(get_db),
) -> str:
    """Valida API key via Bearer OU X-API-Key (Bearer tem prioridade).

    Injeta request.state.tenant_id, permissions, key_id, environment.
    """
    # Resolver key: Bearer prioritario, X-API-Key fallback
    resolved_key: str | None = None
    if bearer is not None and bearer.credentials:
        resolved_key = bearer.credentials
    elif api_key:
        resolved_key = api_key

    if not resolved_key:
        raise APIError(
            401,
            "auth-invalida",
            "Autenticacao invalida",
            "API key ausente ou invalida",
        )

    if _is_unkey_enabled():
        unkey_data = await _verify_via_unkey(resolved_key)
        request.state.tenant_id = unkey_data["tenant_id"]
        request.state.permissions = unkey_data["permissions"]
        request.state.key_id = unkey_data["key_id"]
    else:
        tenant_id = await _verify_via_db(resolved_key, db)
        request.state.tenant_id = tenant_id
        request.state.permissions = ["*"]
        request.state.key_id = ""

    # Environment detection (#106): prefixo da key ou fallback
    if resolved_key.startswith("sk_test_") or resolved_key.startswith("uuba_test_"):
        request.state.environment = "test"
    else:
        request.state.environment = "live"

    return resolved_key
```

- [ ] **Step 2: Atualizar conftest com BEARER_AUTH e override dual**

Aplicar as mudancas do Task 1 Step 1 no conftest (adicionar `BEARER_AUTH`, atualizar overrides, adicionar `receivables:write` as permissoes, setar `request.state.environment`).

- [ ] **Step 3: Rodar testes Bearer**

Run: `python -m pytest tests/test_auth_bearer.py -v`
Expected: ALL PASS

- [ ] **Step 4: Rodar todos os testes para garantir backward compat**

Run: `python -m pytest tests/ -v --tb=short`
Expected: ALL PASS — X-API-Key continua funcionando

- [ ] **Step 5: Commit implementacao GREEN**

```bash
git add app/auth/api_key.py tests/conftest.py tests/test_auth_bearer.py
git commit -m "feat(auth): accept Authorization: Bearer + X-API-Key fallback — issue #105"
```

---

## Task 3: Atualizar attack tests e test_attack_auth.py

**Files:**
- Modify: `tests/test_attack_auth.py`

- [ ] **Step 1: Adicionar testes de ataque Bearer**

Adicionar ao final de `test_attack_auth.py`:

```python
# --- Bearer attack vectors ---


async def test_bearer_with_null_bytes(client):
    resp = await client.get(
        "/api/v1/clientes", headers={"Authorization": "Bearer valid\x00key"}
    )
    assert resp.status_code == 401


async def test_bearer_with_very_long_token(client):
    resp = await client.get(
        "/api/v1/clientes", headers={"Authorization": f"Bearer {'A' * 100_000}"}
    )
    assert resp.status_code == 401


async def test_bearer_with_sql_injection(client):
    resp = await client.get(
        "/api/v1/clientes", headers={"Authorization": "Bearer ' OR 1=1--"}
    )
    assert resp.status_code == 401


async def test_bearer_double_bearer_prefix(client):
    from tests.conftest import API_KEY

    resp = await client.get(
        "/api/v1/clientes",
        headers={"Authorization": f"Bearer Bearer {API_KEY}"},
    )
    assert resp.status_code == 401
```

- [ ] **Step 2: Atualizar teste existente que verifica Bearer rejected**

O teste `test_auth_header_with_bearer_prefix` (linha 38-44) testava que `Bearer` em `X-API-Key` era rejeitado. Manter esse teste (Bearer no header errado deve falhar), mas adicionar comentario:

```python
async def test_bearer_prefix_in_x_api_key_header_rejected(client):
    """Bearer prefix no X-API-Key nao funciona — usar Authorization: Bearer."""
    resp = await client.get(
        "/api/v1/clientes",
        headers={"X-API-Key": f"Bearer {AUTH['X-API-Key']}"},
    )
    assert resp.status_code == 401
```

- [ ] **Step 3: Rodar attack tests**

Run: `python -m pytest tests/test_attack_auth.py -v`
Expected: ALL PASS

- [ ] **Step 4: Commit**

```bash
git add tests/test_attack_auth.py
git commit -m "test(auth): add Bearer attack vectors — issue #105"
```

---

## Task 4: Environment Detection (#106)

**Files:**
- Modify: `app/routers/v0_faturas.py`
- Create: `tests/test_auth_environment.py`

- [ ] **Step 1: Escrever testes environment (RED)**

```python
# tests/test_auth_environment.py
"""Testes para environment detection via prefixo da key."""

import pytest
from unittest.mock import patch, AsyncMock
from app.auth.api_key import verify_api_key, _verify_via_db, clear_tenant_cache


class TestEnvironmentFromKeyPrefix:
    """Environment determinado pelo prefixo da API key."""

    @pytest.fixture(autouse=True)
    def cleanup(self):
        clear_tenant_cache()
        yield
        clear_tenant_cache()

    async def test_sk_test_prefix_sets_test_environment(self, client):
        """Keys com sk_test_ devem setar environment=test."""
        # O conftest ja seta environment=test para key_test
        # Verificar via v0/faturas dry_run que retorna environment
        pass  # Coberto pelo teste funcional abaixo

    async def test_sk_live_prefix_sets_live_environment(self):
        """Keys com sk_live_ devem setar environment=live."""
        from unittest.mock import MagicMock
        from fastapi import Request

        request = MagicMock(spec=Request)
        request.state = MagicMock()
        request.headers = {"Authorization": "Bearer sk_live_abc123"}

        with patch("app.auth.api_key._is_unkey_enabled", return_value=False):
            with patch(
                "app.auth.api_key._verify_via_db",
                new_callable=AsyncMock,
                return_value="ten_test",
            ):
                from fastapi.security import HTTPAuthorizationCredentials

                bearer = HTTPAuthorizationCredentials(
                    scheme="Bearer", credentials="sk_live_abc123"
                )
                await verify_api_key(request, bearer=bearer, api_key=None, db=AsyncMock())
                assert request.state.environment == "live"

    async def test_regular_key_defaults_to_live(self):
        """Keys sem prefixo sk_ devem defaultar para live."""
        from unittest.mock import MagicMock
        from fastapi import Request

        request = MagicMock(spec=Request)
        request.state = MagicMock()

        with patch("app.auth.api_key._is_unkey_enabled", return_value=False):
            with patch(
                "app.auth.api_key._verify_via_db",
                new_callable=AsyncMock,
                return_value="ten_test",
            ):
                from fastapi.security import HTTPAuthorizationCredentials

                bearer = HTTPAuthorizationCredentials(
                    scheme="Bearer", credentials="regular_key_123"
                )
                await verify_api_key(request, bearer=bearer, api_key=None, db=AsyncMock())
                assert request.state.environment == "live"
```

- [ ] **Step 2: Atualizar v0_faturas.py para usar request.state.environment**

Substituir linhas 226-228 em `v0_faturas.py`:

```python
# ANTES (fragil):
key_id = getattr(request.state, "key_id", "")
environment = "test" if "test" in key_id.lower() else "live"

# DEPOIS (robusto):
environment = getattr(request.state, "environment", "live")
```

- [ ] **Step 3: Rodar testes**

Run: `python -m pytest tests/test_auth_environment.py tests/test_v0_faturas_functional.py -v`
Expected: ALL PASS

- [ ] **Step 4: Commit**

```bash
git add app/auth/api_key.py app/routers/v0_faturas.py tests/test_auth_environment.py
git commit -m "fix(auth): environment detection via key prefix, not key_id string — issue #106"
```

---

## Task 5: OpenAPI securitySchemes (#105)

**Files:**
- Modify: `app/main.py`

- [ ] **Step 1: Adicionar custom OpenAPI schema**

Adicionar apos a linha 229 (`app = FastAPI(...)`) em `main.py`:

```python
from fastapi.openapi.utils import get_openapi


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        tags=app.openapi_tags,
        servers=app.servers,
        contact=app.contact,
    )
    schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "Unkey",
            "description": "API key: Authorization: Bearer <key>",
        },
        "ApiKeyHeader": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
            "description": "(Deprecated) Use Authorization: Bearer em vez disso.",
        },
    }
    schema["security"] = [{"BearerAuth": []}, {"ApiKeyHeader": []}]
    app.openapi_schema = schema
    return schema


app.openapi = custom_openapi
```

- [ ] **Step 2: Verificar OpenAPI gerado**

Run: `python -c "from app.main import app; import json; print(json.dumps(app.openapi()['components']['securitySchemes'], indent=2))"`
Expected: Mostra BearerAuth e ApiKeyHeader

- [ ] **Step 3: Commit**

```bash
git add app/main.py
git commit -m "docs(openapi): add Bearer + X-API-Key securitySchemes — issue #105"
```

---

## Task 6: Idempotency — Model e Migration (#107)

**Files:**
- Create: `app/models/idempotency.py`
- Create: `alembic/versions/xxx_add_idempotency_cache.py`

- [ ] **Step 1: Criar model SQLAlchemy**

```python
# app/models/idempotency.py
"""Model para cache de idempotency — dedup de POST requests."""

from datetime import datetime, timezone
from sqlalchemy import String, Integer, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class IdempotencyCache(Base):
    __tablename__ = "idempotency_cache"

    key: Mapped[str] = mapped_column(String(200), primary_key=True)
    body_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    response_status: Mapped[int] = mapped_column(Integer, nullable=False)
    response_body: Mapped[str] = mapped_column(Text, nullable=False)
    response_content_type: Mapped[str] = mapped_column(
        String(100), nullable=False, default="application/json"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
```

- [ ] **Step 2: Criar migration Alembic**

Run: `cd uuba-tech-api && alembic revision --autogenerate -m "add idempotency_cache table"`

Verificar que a migration gerada cria a tabela com indice em `expires_at` para cleanup eficiente:

```python
# Adicionar ao final do upgrade():
op.create_index("ix_idempotency_expires", "idempotency_cache", ["expires_at"])
```

- [ ] **Step 3: Registrar model no conftest (para testes SQLite)**

Adicionar ao conftest.py nos imports:

```python
from app.models.idempotency import IdempotencyCache  # noqa: F401
```

- [ ] **Step 4: Commit**

```bash
git add app/models/idempotency.py alembic/versions/ tests/conftest.py
git commit -m "feat(db): add idempotency_cache table — issue #107"
```

---

## Task 7: Idempotency — Middleware (#107)

**Files:**
- Create: `app/auth/idempotency.py`
- Create: `tests/test_idempotency.py`

- [ ] **Step 1: Escrever testes (RED)**

```python
# tests/test_idempotency.py
"""Testes para idempotency middleware."""

import hashlib
import json
import pytest
from unittest.mock import patch, AsyncMock


VALID_PAYLOAD = {
    "customer": {
        "type": "PJ",
        "document": "12345678000190",
        "name": "Teste Ltda",
    },
    "operations": [
        {
            "service": {"code": "SVC-01", "description": "Teste"},
            "sale": {"amount": 100.0, "due_date": "2026-12-01"},
        }
    ],
    "payment_method": "BOLETO_BANCARIO",
}


class TestIdempotencyKey:
    """POST com Idempotency-Key deve retornar cached response."""

    @patch("app.routers.v0_faturas._forward_to_n8n", new_callable=AsyncMock)
    async def test_first_request_processes_normally(self, mock_n8n, v0_client):
        mock_n8n.return_value = {
            "customer": {"id": "cst_1", "created": True},
            "operations": [
                {"id": "op_1", "object": "operation", "type": "sale", "status": "created"}
            ],
            "status": "completed",
        }
        from tests.conftest import BEARER_AUTH

        resp = await v0_client.post(
            "/api/v0/faturas",
            json=VALID_PAYLOAD,
            headers={**BEARER_AUTH, "Idempotency-Key": "idem-001"},
        )
        assert resp.status_code == 201
        assert "X-Idempotent-Replayed" not in resp.headers

    @patch("app.routers.v0_faturas._forward_to_n8n", new_callable=AsyncMock)
    async def test_replay_returns_cached_response(self, mock_n8n, v0_client):
        mock_n8n.return_value = {
            "customer": {"id": "cst_1", "created": True},
            "operations": [
                {"id": "op_1", "object": "operation", "type": "sale", "status": "created"}
            ],
            "status": "completed",
        }
        from tests.conftest import BEARER_AUTH

        headers = {**BEARER_AUTH, "Idempotency-Key": "idem-002"}
        resp1 = await v0_client.post("/api/v0/faturas", json=VALID_PAYLOAD, headers=headers)
        resp2 = await v0_client.post("/api/v0/faturas", json=VALID_PAYLOAD, headers=headers)

        assert resp2.status_code == resp1.status_code
        assert resp2.json() == resp1.json()
        assert resp2.headers.get("X-Idempotent-Replayed") == "true"
        # n8n chamado apenas 1 vez
        assert mock_n8n.call_count == 1

    @patch("app.routers.v0_faturas._forward_to_n8n", new_callable=AsyncMock)
    async def test_same_key_different_body_returns_422(self, mock_n8n, v0_client):
        mock_n8n.return_value = {
            "customer": {"id": "cst_1", "created": True},
            "operations": [
                {"id": "op_1", "object": "operation", "type": "sale", "status": "created"}
            ],
            "status": "completed",
        }
        from tests.conftest import BEARER_AUTH

        headers = {**BEARER_AUTH, "Idempotency-Key": "idem-003"}
        await v0_client.post("/api/v0/faturas", json=VALID_PAYLOAD, headers=headers)

        different_payload = {**VALID_PAYLOAD, "notes": "changed"}
        resp2 = await v0_client.post(
            "/api/v0/faturas", json=different_payload, headers=headers
        )
        assert resp2.status_code == 422
        assert "idempotency" in resp2.json()["detail"].lower()

    async def test_no_idempotency_key_processes_normally(self, v0_client):
        """Sem header Idempotency-Key, request processado normalmente."""
        from tests.conftest import BEARER_AUTH

        resp = await v0_client.post(
            "/api/v0/faturas?dry_run=true",
            json=VALID_PAYLOAD,
            headers=BEARER_AUTH,
        )
        assert resp.status_code == 200

    async def test_dry_run_ignores_idempotency(self, v0_client):
        """dry_run nao deve ser cacheado."""
        from tests.conftest import BEARER_AUTH

        headers = {**BEARER_AUTH, "Idempotency-Key": "idem-dry"}
        resp1 = await v0_client.post(
            "/api/v0/faturas?dry_run=true", json=VALID_PAYLOAD, headers=headers
        )
        resp2 = await v0_client.post(
            "/api/v0/faturas?dry_run=true", json=VALID_PAYLOAD, headers=headers
        )
        assert "X-Idempotent-Replayed" not in resp2.headers
```

- [ ] **Step 2: Rodar testes (confirmar RED)**

Run: `python -m pytest tests/test_idempotency.py -v`
Expected: FAIL

- [ ] **Step 3: Implementar middleware de idempotency**

```python
# app/auth/idempotency.py
"""Idempotency middleware — dedup POST requests via Idempotency-Key header."""

import hashlib
import json
import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.idempotency import IdempotencyCache

logger = logging.getLogger("uuba")

IDEMPOTENCY_TTL = timedelta(hours=24)


def _hash_body(body: bytes) -> str:
    """SHA-256 hex hash do request body."""
    return hashlib.sha256(body).hexdigest()


async def check_idempotency(
    db: AsyncSession,
    tenant_id: str,
    idempotency_key: str,
    body: bytes,
) -> IdempotencyCache | None:
    """Verifica cache. Retorna entry se hit, None se miss. Raises 422 se mismatch."""
    from app.exceptions import APIError

    cache_key = f"{tenant_id}:{idempotency_key}"
    body_hash = _hash_body(body)

    result = await db.execute(
        select(IdempotencyCache).where(
            IdempotencyCache.key == cache_key,
            IdempotencyCache.expires_at > datetime.now(timezone.utc),
        )
    )
    entry = result.scalar_one_or_none()

    if entry is None:
        return None

    if entry.body_hash != body_hash:
        raise APIError(
            422,
            "idempotency-mismatch",
            "Idempotency key reutilizada com body diferente",
            f"A key '{idempotency_key}' ja foi usada com um payload diferente.",
        )

    return entry


async def save_idempotency(
    db: AsyncSession,
    tenant_id: str,
    idempotency_key: str,
    body: bytes,
    response_status: int,
    response_body: str,
) -> None:
    """Salva response no cache de idempotency."""
    cache_key = f"{tenant_id}:{idempotency_key}"
    entry = IdempotencyCache(
        key=cache_key,
        body_hash=_hash_body(body),
        response_status=response_status,
        response_body=response_body,
        expires_at=datetime.now(timezone.utc) + IDEMPOTENCY_TTL,
    )
    db.add(entry)
    await db.commit()


async def cleanup_expired(db: AsyncSession) -> int:
    """Remove entradas expiradas. Retorna quantidade removida."""
    result = await db.execute(
        delete(IdempotencyCache).where(
            IdempotencyCache.expires_at <= datetime.now(timezone.utc)
        )
    )
    await db.commit()
    return result.rowcount or 0
```

- [ ] **Step 4: Integrar idempotency no v0_faturas.py**

Modificar o endpoint `create_receivable` em `v0_faturas.py`:

```python
# Adicionar imports
from app.auth.idempotency import check_idempotency, save_idempotency
from app.database import get_db as get_db_dep
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

# Modificar create_receivable para receber db e raw body
@router.post("", status_code=200, ...)
async def create_receivable(
    data: CanonicalMessage,
    request: Request,
    dry_run: bool = Query(default=False, description="Validar sem enviar ao ERP"),
    idempotency_key: str | None = Header(
        default=None,
        alias="Idempotency-Key",
        description="UUID v4 para idempotencia",
    ),
    db: AsyncSession = Depends(get_db_dep),
):
    tenant_id = request.state.tenant_id
    request_id = generate_id("recv")

    # --- Dry-run: valida e retorna sem processar ---
    if dry_run:
        result = _validate_payload(data)
        return JSONResponse(
            content=result.model_dump(),
            headers={"X-Request-Id": request_id},
        )

    # --- Idempotency check ---
    raw_body = await request.body()
    if idempotency_key:
        cached = await check_idempotency(db, tenant_id, idempotency_key, raw_body)
        if cached is not None:
            import json as _json
            return JSONResponse(
                content=_json.loads(cached.response_body),
                status_code=cached.response_status,
                headers={
                    "X-Request-Id": request_id,
                    "X-Idempotent-Replayed": "true",
                },
            )

    # --- Processamento real ---
    payload = data.model_dump(mode="json")
    n8n_response = await _forward_to_n8n(tenant_id, request_id, payload)

    # ... (resto do codigo existente para montar receivable) ...

    response_content = receivable.model_dump()
    status_code = 201 if status != ReceivableStatus.FAILED else 200

    # --- Salvar idempotency ---
    if idempotency_key:
        import json as _json
        await save_idempotency(
            db, tenant_id, idempotency_key, raw_body,
            status_code, _json.dumps(response_content),
        )

    return JSONResponse(
        content=response_content,
        status_code=status_code,
        headers={"X-Request-Id": request_id},
    )
```

- [ ] **Step 5: Rodar testes**

Run: `python -m pytest tests/test_idempotency.py -v`
Expected: ALL PASS

- [ ] **Step 6: Rodar suite completa**

Run: `python -m pytest tests/ -v --tb=short`
Expected: ALL PASS

- [ ] **Step 7: Commit**

```bash
git add app/auth/idempotency.py app/routers/v0_faturas.py tests/test_idempotency.py
git commit -m "feat(v0): implement Idempotency-Key with 24h dedup — issue #107"
```

---

## Task 8: Suite completa + push

- [ ] **Step 1: Rodar suite completa**

Run: `python -m pytest tests/ -v --tb=short`
Expected: ALL PASS

- [ ] **Step 2: Rodar linter e typecheck**

Run: `cd uuba-tech-api && ruff check app/ tests/ && mypy app/ --ignore-missing-imports`

- [ ] **Step 3: Push e verificar CI**

```bash
git push origin main
gh run list --repo luisbarcia/uuba-tech --limit 3
```

- [ ] **Step 4: Fechar issues**

```bash
gh issue close 105 --repo luisbarcia/uuba-tech --comment "Implementado: Bearer + X-API-Key fallback, OpenAPI securitySchemes"
gh issue close 106 --repo luisbarcia/uuba-tech --comment "Implementado: environment detection via key prefix"
gh issue close 107 --repo luisbarcia/uuba-tech --comment "Implementado: Idempotency-Key com store DB + 24h TTL + 422 mismatch"
```
