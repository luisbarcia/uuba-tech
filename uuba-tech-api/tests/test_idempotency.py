"""Testes para idempotency middleware — dedup via Idempotency-Key header."""

import pytest
from unittest.mock import patch, AsyncMock

from tests.conftest import BEARER_AUTH


VALID_PAYLOAD = {
    "customer": {"type": "PJ", "document": "12345678000190", "name": "Teste Ltda"},
    "operations": [
        {
            "service": {"code": "SVC-01", "description": "Teste"},
            "sale": {"amount": 100.0, "due_date": "2026-12-01"},
        }
    ],
    "payment_method": "BOLETO_BANCARIO",
}

N8N_SUCCESS = {
    "customer": {"id": "cst_1", "created": True},
    "operations": [
        {"id": "op_1", "object": "operation", "type": "sale", "status": "created"}
    ],
    "status": "completed",
}


class TestIdempotencyKey:

    @patch("app.routers.v0_faturas._forward_to_n8n", new_callable=AsyncMock)
    async def test_first_request_processes_normally(self, mock_n8n, v0_client):
        mock_n8n.return_value = N8N_SUCCESS
        resp = await v0_client.post(
            "/api/v0/faturas",
            json=VALID_PAYLOAD,
            headers={**BEARER_AUTH, "Idempotency-Key": "idem-001"},
        )
        assert resp.status_code == 201
        assert "x-idempotent-replayed" not in resp.headers
        assert mock_n8n.call_count == 1

    @patch("app.routers.v0_faturas._forward_to_n8n", new_callable=AsyncMock)
    async def test_replay_returns_cached_response(self, mock_n8n, v0_client):
        mock_n8n.return_value = N8N_SUCCESS
        headers = {**BEARER_AUTH, "Idempotency-Key": "idem-002"}

        resp1 = await v0_client.post("/api/v0/faturas", json=VALID_PAYLOAD, headers=headers)
        resp2 = await v0_client.post("/api/v0/faturas", json=VALID_PAYLOAD, headers=headers)

        assert resp1.status_code == 201
        assert resp2.status_code == 201
        assert resp2.json() == resp1.json()
        assert resp2.headers.get("x-idempotent-replayed") == "true"
        assert mock_n8n.call_count == 1

    @patch("app.routers.v0_faturas._forward_to_n8n", new_callable=AsyncMock)
    async def test_same_key_different_body_returns_422(self, mock_n8n, v0_client):
        mock_n8n.return_value = N8N_SUCCESS
        headers = {**BEARER_AUTH, "Idempotency-Key": "idem-003"}

        await v0_client.post("/api/v0/faturas", json=VALID_PAYLOAD, headers=headers)

        different = {**VALID_PAYLOAD, "notes": "changed body"}
        resp2 = await v0_client.post("/api/v0/faturas", json=different, headers=headers)

        assert resp2.status_code == 422
        body = resp2.json()
        assert "idempotency-mismatch" in body.get("type", "")

    @patch("app.routers.v0_faturas._forward_to_n8n", new_callable=AsyncMock)
    async def test_no_key_always_processes(self, mock_n8n, v0_client):
        mock_n8n.return_value = N8N_SUCCESS

        resp1 = await v0_client.post("/api/v0/faturas", json=VALID_PAYLOAD, headers=BEARER_AUTH)
        resp2 = await v0_client.post("/api/v0/faturas", json=VALID_PAYLOAD, headers=BEARER_AUTH)

        assert resp1.status_code == 201
        assert resp2.status_code == 201
        assert mock_n8n.call_count == 2

    async def test_dry_run_ignores_idempotency(self, v0_client):
        headers = {**BEARER_AUTH, "Idempotency-Key": "idem-dry"}

        resp1 = await v0_client.post(
            "/api/v0/faturas?dry_run=true", json=VALID_PAYLOAD, headers=headers
        )
        resp2 = await v0_client.post(
            "/api/v0/faturas?dry_run=true", json=VALID_PAYLOAD, headers=headers
        )

        assert resp1.status_code == 200
        assert resp2.status_code == 200
        assert "x-idempotent-replayed" not in resp2.headers

    @patch("app.routers.v0_faturas._forward_to_n8n", new_callable=AsyncMock)
    async def test_different_keys_process_independently(self, mock_n8n, v0_client):
        mock_n8n.return_value = N8N_SUCCESS

        resp1 = await v0_client.post(
            "/api/v0/faturas",
            json=VALID_PAYLOAD,
            headers={**BEARER_AUTH, "Idempotency-Key": "key-a"},
        )
        resp2 = await v0_client.post(
            "/api/v0/faturas",
            json=VALID_PAYLOAD,
            headers={**BEARER_AUTH, "Idempotency-Key": "key-b"},
        )

        assert resp1.status_code == 201
        assert resp2.status_code == 201
        assert mock_n8n.call_count == 2
