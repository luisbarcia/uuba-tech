"""Testes do modulo de autenticacao Unkey.

Testa a logica de verify_api_key com Unkey habilitado/desabilitado.
Em ambiente de teste (TESTING=1), o Unkey fica desabilitado por padrao.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.auth.api_key import (
    _is_unkey_enabled,
    _verify_via_unkey,
    _unkey_cache,
    clear_tenant_cache,
)
from app.exceptions import APIError


class TestUnkeyEnabled:
    def test_disabled_in_testing(self):
        """Unkey desabilitado quando TESTING=1."""
        assert _is_unkey_enabled() is False

    @patch.dict("os.environ", {"TESTING": "0", "UNKEY_ENABLED": "true"})
    def test_enabled_with_env_var(self):
        assert _is_unkey_enabled() is True

    @patch.dict("os.environ", {"TESTING": "0", "UNKEY_ENABLED": "1"})
    def test_enabled_with_1(self):
        assert _is_unkey_enabled() is True

    @patch.dict("os.environ", {"TESTING": "0", "UNKEY_ENABLED": ""})
    def test_disabled_with_empty(self):
        assert _is_unkey_enabled() is False

    @patch.dict("os.environ", {"TESTING": "0"})
    def test_disabled_without_env_var(self):
        assert _is_unkey_enabled() is False


class TestVerifyViaUnkey:
    @pytest.fixture(autouse=True)
    def cleanup_cache(self):
        clear_tenant_cache()
        yield
        clear_tenant_cache()

    @pytest.fixture(autouse=True)
    def mock_root_key(self):
        """Todos os testes de _verify_via_unkey precisam de UNKEY_ROOT_KEY setado."""
        with patch("app.auth.api_key.UNKEY_ROOT_KEY", "unkey_root_test"):
            yield

    @pytest.mark.asyncio
    async def test_valid_key_returns_tenant_data(self):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "valid": True,
            "keyId": "key_test123",
            "ownerId": "ten_abc123",
            "permissions": ["receivables:write"],
        }

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(return_value=mock_response)

        with patch("app.auth.api_key.httpx.AsyncClient", return_value=mock_client):
            result = await _verify_via_unkey("uuba_live_test_key")

        assert result["tenant_id"] == "ten_abc123"
        assert result["permissions"] == ["receivables:write"]
        assert result["key_id"] == "key_test123"

    @pytest.mark.asyncio
    async def test_invalid_key_raises_401(self):
        mock_response = MagicMock()
        mock_response.json.return_value = {"valid": False}

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(return_value=mock_response)

        with patch("app.auth.api_key.httpx.AsyncClient", return_value=mock_client):
            with pytest.raises(APIError) as exc_info:
                await _verify_via_unkey("invalid_key")
            assert exc_info.value.status == 401

    @pytest.mark.asyncio
    async def test_missing_owner_id_raises_401(self):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "valid": True,
            "keyId": "key_test123",
            "ownerId": "",
            "permissions": [],
        }

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(return_value=mock_response)

        with patch("app.auth.api_key.httpx.AsyncClient", return_value=mock_client):
            with pytest.raises(APIError) as exc_info:
                await _verify_via_unkey("key_no_owner")
            assert exc_info.value.status == 401

    @pytest.mark.asyncio
    async def test_cache_hit_avoids_http_call(self):
        """Segunda chamada com mesma key usa cache."""
        import time

        _unkey_cache["cached_key"] = (
            {
                "tenant_id": "ten_cached",
                "permissions": [],
                "key_id": "key_cached",
            },
            time.monotonic(),
        )

        result = await _verify_via_unkey("cached_key")
        assert result["tenant_id"] == "ten_cached"

    @pytest.mark.asyncio
    async def test_v2_envelope_meta_data(self):
        """v2: response envelopada em {meta, data} (#78)."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "meta": {"requestId": "req_test"},
            "data": {
                "valid": True,
                "keyId": "key_v2",
                "identity": {"id": "id_001", "externalId": "ten_v2"},
                "permissions": ["clients:read"],
            },
        }

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(return_value=mock_response)

        with patch("app.auth.api_key.httpx.AsyncClient", return_value=mock_client):
            result = await _verify_via_unkey("uuba_live_v2_key")

        assert result["tenant_id"] == "ten_v2"
        assert result["permissions"] == ["clients:read"]
        assert result["key_id"] == "key_v2"

    @pytest.mark.asyncio
    async def test_v2_identity_externalid_over_ownerid(self):
        """v2: identity.externalId tem prioridade sobre ownerId (#79)."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "meta": {"requestId": "req_test"},
            "data": {
                "valid": True,
                "keyId": "key_both",
                "ownerId": "ten_old",
                "identity": {"id": "id_002", "externalId": "ten_new"},
                "permissions": [],
            },
        }

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(return_value=mock_response)

        with patch("app.auth.api_key.httpx.AsyncClient", return_value=mock_client):
            result = await _verify_via_unkey("uuba_live_both")

        assert result["tenant_id"] == "ten_new"  # identity tem prioridade

    @pytest.mark.asyncio
    async def test_v2_no_identity_falls_back_to_ownerid(self):
        """v2: sem identity, faz fallback para ownerId (backward compat)."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "valid": True,
                "keyId": "key_legacy",
                "ownerId": "ten_legacy",
                "permissions": [],
            },
        }

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(return_value=mock_response)

        with patch("app.auth.api_key.httpx.AsyncClient", return_value=mock_client):
            result = await _verify_via_unkey("uuba_live_legacy")

        assert result["tenant_id"] == "ten_legacy"

    @pytest.mark.asyncio
    async def test_v2_sends_authorization_header(self):
        """v2: envia Authorization: Bearer root_key (#77)."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "valid": True,
                "keyId": "key_auth",
                "identity": {"id": "id_003", "externalId": "ten_auth"},
                "permissions": [],
            },
        }

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(return_value=mock_response)

        with patch("app.auth.api_key.httpx.AsyncClient", return_value=mock_client):
            await _verify_via_unkey("uuba_live_auth_test")

        call_kwargs = mock_client.post.call_args
        assert call_kwargs[1]["headers"]["Authorization"] == "Bearer unkey_root_test"

    @pytest.mark.asyncio
    async def test_http_error_raises_503(self):
        import httpx

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(side_effect=httpx.HTTPError("connection failed"))

        with patch("app.auth.api_key.httpx.AsyncClient", return_value=mock_client):
            with pytest.raises(APIError) as exc_info:
                await _verify_via_unkey("key_http_fail")
            assert exc_info.value.status == 503
            assert exc_info.value.error_type == "auth-indisponivel"
