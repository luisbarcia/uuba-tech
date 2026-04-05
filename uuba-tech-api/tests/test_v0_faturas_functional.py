"""Testes funcionais para POST /api/v0/faturas.

Cobre: dry_run, validacao 422, processamento real (mock httpx), headers.
Issue: #96
"""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
from fastapi import Request
from httpx import ASGITransport, AsyncClient

from app.auth.api_key import clear_tenant_cache, verify_api_key
from app.config import settings
from app.database import get_db
from app.exceptions import APIError
from app.main import app
from tests.conftest import AUTH, TEST_TENANT_ID

# ---------------------------------------------------------------------------
# Payload base
# ---------------------------------------------------------------------------

MINIMAL_PAYLOAD = {
    "customer": {
        "type": "PJ",
        "document": "12345678000190",
        "name": "Padaria Bom Pao",
    },
    "operations": [
        {
            "service": {"description": "Consultoria", "code": "SRV001"},
            "sale": {"amount": 1500.00, "due_date": "2026-05-01"},
        }
    ],
    "payment_method": "BOLETO_BANCARIO",
}


# ---------------------------------------------------------------------------
# Helpers para mock httpx
# ---------------------------------------------------------------------------


def _n8n_success_response() -> MagicMock:
    """Mock de resposta n8n com formato Receivable completo."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "customer": {"id": "cst_123abc", "created": True},
        "operations": [{"id": "op_abc123", "type": "sale", "status": "created"}],
        "status": "completed",
    }
    return mock_resp


def _n8n_fallback_response() -> MagicMock:
    """Mock de resposta n8n em formato diferente (sem customer/operations)."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "customer_id": "cst_fallback",
        "customer_created": True,
        "operation_ids": ["op_fall1"],
        "status": "completed",
    }
    return mock_resp


def _mock_httpx_client(mock_response=None, side_effect=None) -> AsyncMock:
    """Cria um AsyncClient mockado para httpx."""
    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    if side_effect:
        mock_client.post = AsyncMock(side_effect=side_effect)
    else:
        mock_client.post = AsyncMock(return_value=mock_response)
    return mock_client


# ===========================================================================
# 1. dry_run=true (sem mock de httpx necessario)
# ===========================================================================


async def test_dry_run_valid_payload(v0_client):
    resp = await v0_client.post("/api/v0/faturas?dry_run=true", json=MINIMAL_PAYLOAD, headers=AUTH)
    assert resp.status_code == 200
    body = resp.json()
    assert body["object"] == "validation_result"
    assert body["valid"] is True
    assert body["customer_type"] == "PJ"
    assert body["operations_count"] == 1
    assert body["total_sales"] == 1
    assert body["total_value"] == 1500.00


async def test_dry_run_warnings_missing_email(v0_client):
    resp = await v0_client.post("/api/v0/faturas?dry_run=true", json=MINIMAL_PAYLOAD, headers=AUTH)
    assert resp.status_code == 200
    codes = [w["code"] for w in resp.json()["warnings"]]
    assert "missing_email" in codes


async def test_dry_run_warnings_missing_phone(v0_client):
    resp = await v0_client.post("/api/v0/faturas?dry_run=true", json=MINIMAL_PAYLOAD, headers=AUTH)
    assert resp.status_code == 200
    codes = [w["code"] for w in resp.json()["warnings"]]
    assert "missing_phone" in codes


async def test_dry_run_no_warning_when_email_present(v0_client):
    payload = {
        **MINIMAL_PAYLOAD,
        "customer": {**MINIMAL_PAYLOAD["customer"], "email": "padaria@email.com"},
    }
    resp = await v0_client.post("/api/v0/faturas?dry_run=true", json=payload, headers=AUTH)
    assert resp.status_code == 200
    codes = [w["code"] for w in resp.json()["warnings"]]
    assert "missing_email" not in codes


async def test_dry_run_counts_operations(v0_client):
    payload = {
        **MINIMAL_PAYLOAD,
        "operations": [
            {
                "service": {"description": "Consultoria", "code": "SRV001"},
                "sale": {"amount": 1000.00, "due_date": "2026-05-01"},
            },
            {
                "service": {"description": "Suporte", "code": "SRV002"},
                "sale": {"amount": 500.00, "due_date": "2026-06-01"},
            },
            {
                "service": {"description": "Treinamento", "code": "SRV003"},
                "sale": {"amount": 750.00, "due_date": "2026-07-01"},
            },
        ],
    }
    resp = await v0_client.post("/api/v0/faturas?dry_run=true", json=payload, headers=AUTH)
    assert resp.status_code == 200
    body = resp.json()
    assert body["operations_count"] == 3
    assert body["total_sales"] == 3
    assert body["total_value"] == 2250.00


# ===========================================================================
# 2. Validacao 422
# ===========================================================================


async def test_missing_customer(v0_client):
    payload = {
        "operations": MINIMAL_PAYLOAD["operations"],
        "payment_method": "BOLETO_BANCARIO",
    }
    resp = await v0_client.post("/api/v0/faturas", json=payload, headers=AUTH)
    assert resp.status_code == 422


async def test_missing_operations(v0_client):
    payload = {
        "customer": MINIMAL_PAYLOAD["customer"],
        "payment_method": "BOLETO_BANCARIO",
    }
    resp = await v0_client.post("/api/v0/faturas", json=payload, headers=AUTH)
    assert resp.status_code == 422


async def test_empty_operations(v0_client):
    payload = {**MINIMAL_PAYLOAD, "operations": []}
    resp = await v0_client.post("/api/v0/faturas", json=payload, headers=AUTH)
    assert resp.status_code == 422


async def test_invalid_payment_method(v0_client):
    payload = {**MINIMAL_PAYLOAD, "payment_method": "PIX"}
    resp = await v0_client.post("/api/v0/faturas", json=payload, headers=AUTH)
    assert resp.status_code == 422


async def test_invalid_customer_type(v0_client):
    payload = {
        **MINIMAL_PAYLOAD,
        "customer": {"type": "LTDA", "document": "12345678000190", "name": "Empresa X"},
    }
    resp = await v0_client.post("/api/v0/faturas", json=payload, headers=AUTH)
    assert resp.status_code == 422


async def test_extra_fields_rejected(v0_client):
    payload = {**MINIMAL_PAYLOAD, "campo_extra_inexistente": "valor"}
    resp = await v0_client.post("/api/v0/faturas", json=payload, headers=AUTH)
    assert resp.status_code == 422


async def test_sale_amount_zero(v0_client):
    payload = {
        **MINIMAL_PAYLOAD,
        "operations": [
            {
                "service": {"description": "Consultoria", "code": "SRV001"},
                "sale": {"amount": 0, "due_date": "2026-05-01"},
            }
        ],
    }
    resp = await v0_client.post("/api/v0/faturas", json=payload, headers=AUTH)
    assert resp.status_code == 422


async def test_sale_amount_negative(v0_client):
    payload = {
        **MINIMAL_PAYLOAD,
        "operations": [
            {
                "service": {"description": "Consultoria", "code": "SRV001"},
                "sale": {"amount": -100, "due_date": "2026-05-01"},
            }
        ],
    }
    resp = await v0_client.post("/api/v0/faturas", json=payload, headers=AUTH)
    assert resp.status_code == 422


# ===========================================================================
# 3. Processamento real (mock httpx)
# ===========================================================================


async def test_forward_to_n8n_success(v0_client):
    mock_client = _mock_httpx_client(mock_response=_n8n_success_response())

    with patch("app.routers.v0_faturas.httpx.AsyncClient", return_value=mock_client):
        resp = await v0_client.post("/api/v0/faturas", json=MINIMAL_PAYLOAD, headers=AUTH)

    assert resp.status_code == 201
    body = resp.json()
    assert body["object"] == "receivable"
    assert body["status"] == "completed"
    assert body["customer"]["id"] == "cst_123abc"
    assert body["customer"]["created"] is True
    assert len(body["operations"]) == 1
    assert body["operations"][0]["id"] == "op_abc123"
    assert body["operations"][0]["type"] == "sale"
    assert body["operations"][0]["status"] == "created"


async def test_n8n_timeout(v0_client):
    mock_client = _mock_httpx_client(side_effect=httpx.TimeoutException("timeout"))

    with patch("app.routers.v0_faturas.httpx.AsyncClient", return_value=mock_client):
        resp = await v0_client.post("/api/v0/faturas", json=MINIMAL_PAYLOAD, headers=AUTH)

    assert resp.status_code == 504
    assert resp.json()["type"] == "https://api.uubatech.com/errors/n8n-timeout"


async def test_n8n_error_response(v0_client):
    mock_resp = MagicMock()
    mock_resp.status_code = 500
    mock_resp.text = "Internal Server Error"
    mock_client = _mock_httpx_client(mock_response=mock_resp)

    with patch("app.routers.v0_faturas.httpx.AsyncClient", return_value=mock_client):
        resp = await v0_client.post("/api/v0/faturas", json=MINIMAL_PAYLOAD, headers=AUTH)

    assert resp.status_code == 502
    assert resp.json()["type"] == "https://api.uubatech.com/errors/n8n-error"


async def test_n8n_connection_error(v0_client):
    mock_client = _mock_httpx_client(side_effect=httpx.ConnectError("connection refused"))

    with patch("app.routers.v0_faturas.httpx.AsyncClient", return_value=mock_client):
        resp = await v0_client.post("/api/v0/faturas", json=MINIMAL_PAYLOAD, headers=AUTH)

    assert resp.status_code == 502
    assert resp.json()["type"] == "https://api.uubatech.com/errors/n8n-unavailable"


async def test_n8n_fallback_response(v0_client):
    """n8n retorna formato diferente (sem customer/operations) — usa fallback."""
    mock_client = _mock_httpx_client(mock_response=_n8n_fallback_response())

    with patch("app.routers.v0_faturas.httpx.AsyncClient", return_value=mock_client):
        resp = await v0_client.post("/api/v0/faturas", json=MINIMAL_PAYLOAD, headers=AUTH)

    assert resp.status_code == 201
    body = resp.json()
    assert body["object"] == "receivable"
    assert body["customer"]["id"] == "cst_fallback"
    assert body["customer"]["created"] is True
    assert len(body["operations"]) == 1
    assert body["operations"][0]["type"] == "sale"
    assert body["operations"][0]["status"] == "created"


# ===========================================================================
# 4. Headers
# ===========================================================================


async def test_request_id_header_dry_run(v0_client):
    resp = await v0_client.post("/api/v0/faturas?dry_run=true", json=MINIMAL_PAYLOAD, headers=AUTH)
    assert resp.status_code == 200
    assert "x-request-id" in resp.headers
    assert resp.headers["x-request-id"].startswith("recv_")


async def test_request_id_header_real(v0_client):
    mock_client = _mock_httpx_client(mock_response=_n8n_success_response())

    with patch("app.routers.v0_faturas.httpx.AsyncClient", return_value=mock_client):
        resp = await v0_client.post("/api/v0/faturas", json=MINIMAL_PAYLOAD, headers=AUTH)

    assert resp.status_code == 201
    assert "x-request-id" in resp.headers
    assert resp.headers["x-request-id"].startswith("recv_")


async def test_environment_test_from_key(v0_client):
    """key_id contendo 'test' → environment='test'."""
    mock_client = _mock_httpx_client(mock_response=_n8n_success_response())

    with patch("app.routers.v0_faturas.httpx.AsyncClient", return_value=mock_client):
        resp = await v0_client.post("/api/v0/faturas", json=MINIMAL_PAYLOAD, headers=AUTH)

    assert resp.status_code == 201
    # v0_client fixture seta key_id="key_test" → environment="test"
    assert resp.json()["environment"] == "test"


async def test_environment_live_when_no_test_in_key(engine):
    """key_id sem 'test' → environment='live'.

    Usa override inline com key_id diferente para testar environment='live'.
    """
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

    from app.database import (
        get_cliente_repository,
        get_cobranca_repository,
        get_fatura_repository,
    )
    from app.infrastructure.repositories.sqlalchemy_cliente_repo import (
        SqlAlchemyClienteRepository,
    )
    from app.infrastructure.repositories.sqlalchemy_cobranca_repo import (
        SqlAlchemyCobrancaRepository,
    )
    from app.infrastructure.repositories.sqlalchemy_fatura_repo import (
        SqlAlchemyFaturaRepository,
    )

    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        async with factory() as session:
            yield session

    async def override_fatura_repo():
        async with factory() as session:
            yield SqlAlchemyFaturaRepository(session, TEST_TENANT_ID)

    async def override_cobranca_repo():
        async with factory() as session:
            yield SqlAlchemyCobrancaRepository(session, TEST_TENANT_ID)

    async def override_cliente_repo():
        async with factory() as session:
            yield SqlAlchemyClienteRepository(session, TEST_TENANT_ID)

    async def override_verify_live(request: Request):
        api_key = request.headers.get("X-API-Key", "")
        if not api_key or api_key != settings.api_key:
            raise APIError(
                401, "auth-invalida", "Autenticacao invalida", "API key ausente ou invalida"
            )
        request.state.tenant_id = TEST_TENANT_ID
        request.state.permissions = ["receivables:write"]
        request.state.key_id = "key_live_prod_abc"  # sem "test"
        return api_key

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_fatura_repository] = override_fatura_repo
    app.dependency_overrides[get_cobranca_repository] = override_cobranca_repo
    app.dependency_overrides[get_cliente_repository] = override_cliente_repo
    app.dependency_overrides[verify_api_key] = override_verify_live
    clear_tenant_cache()

    mock_client = _mock_httpx_client(mock_response=_n8n_success_response())

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as ac:
            with patch("app.routers.v0_faturas.httpx.AsyncClient", return_value=mock_client):
                resp = await ac.post("/api/v0/faturas", json=MINIMAL_PAYLOAD, headers=AUTH)

        assert resp.status_code == 201
        assert resp.json()["environment"] == "live"
    finally:
        app.dependency_overrides.clear()
        clear_tenant_cache()
