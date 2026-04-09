"""Testes para environment detection via prefixo da API key."""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from fastapi import Request
from app.auth.api_key import verify_api_key, clear_tenant_cache


class TestEnvironmentFromKeyPrefix:
    """Environment determinado pelo prefixo da API key."""

    @pytest.fixture(autouse=True)
    def cleanup(self):
        clear_tenant_cache()
        yield
        clear_tenant_cache()

    async def test_sk_live_prefix_sets_live(self):
        request = MagicMock(spec=Request)
        request.state = MagicMock()

        with patch("app.auth.api_key._is_unkey_enabled", return_value=False):
            with patch(
                "app.auth.api_key._verify_via_db",
                new_callable=AsyncMock,
                return_value="ten_test",
            ):
                from fastapi.security import HTTPAuthorizationCredentials
                bearer = HTTPAuthorizationCredentials(scheme="Bearer", credentials="sk_live_abc123")
                await verify_api_key(request, bearer=bearer, api_key=None, db=AsyncMock())
                assert request.state.environment == "live"

    async def test_sk_test_prefix_sets_test(self):
        request = MagicMock(spec=Request)
        request.state = MagicMock()

        with patch("app.auth.api_key._is_unkey_enabled", return_value=False):
            with patch(
                "app.auth.api_key._verify_via_db",
                new_callable=AsyncMock,
                return_value="ten_test",
            ):
                from fastapi.security import HTTPAuthorizationCredentials
                bearer = HTTPAuthorizationCredentials(scheme="Bearer", credentials="sk_test_xyz789")
                await verify_api_key(request, bearer=bearer, api_key=None, db=AsyncMock())
                assert request.state.environment == "test"

    async def test_uuba_test_prefix_sets_test(self):
        request = MagicMock(spec=Request)
        request.state = MagicMock()

        with patch("app.auth.api_key._is_unkey_enabled", return_value=False):
            with patch(
                "app.auth.api_key._verify_via_db",
                new_callable=AsyncMock,
                return_value="ten_test",
            ):
                from fastapi.security import HTTPAuthorizationCredentials
                bearer = HTTPAuthorizationCredentials(scheme="Bearer", credentials="uuba_test_abc")
                await verify_api_key(request, bearer=bearer, api_key=None, db=AsyncMock())
                assert request.state.environment == "test"

    async def test_regular_key_defaults_to_live(self):
        request = MagicMock(spec=Request)
        request.state = MagicMock()

        with patch("app.auth.api_key._is_unkey_enabled", return_value=False):
            with patch(
                "app.auth.api_key._verify_via_db",
                new_callable=AsyncMock,
                return_value="ten_test",
            ):
                from fastapi.security import HTTPAuthorizationCredentials
                bearer = HTTPAuthorizationCredentials(scheme="Bearer", credentials="regular_key")
                await verify_api_key(request, bearer=bearer, api_key=None, db=AsyncMock())
                assert request.state.environment == "live"
