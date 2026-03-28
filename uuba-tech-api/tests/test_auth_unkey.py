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
        _unkey_cache["cached_key"] = ({
            "tenant_id": "ten_cached",
            "permissions": [],
            "key_id": "key_cached",
        }, time.monotonic())

        result = await _verify_via_unkey("cached_key")
        assert result["tenant_id"] == "ten_cached"

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
