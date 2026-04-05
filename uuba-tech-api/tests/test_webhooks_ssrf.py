"""Testes de protecao SSRF para webhooks.

Valida que URLs apontando para hosts internos sao bloqueadas:
- Hostnames literais (localhost, metadata, etc.)
- RFC 1918 ranges (10.x, 172.16.x, 192.168.x)
- IPv6 privados (::1, fc00::, fe80::)
- Bypass por octal, decimal inteiro e hex
- URLs validas continuam funcionando
"""

from unittest.mock import patch

import pytest

from tests.conftest import AUTH


# --- Hosts bloqueados por hostname literal ---


class TestSSRFBlockedHosts:
    """URLs com hostnames literais bloqueados devem retornar 422."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "host",
        [
            "localhost",
            "127.0.0.1",
            "0.0.0.0",
            "169.254.169.254",
            "100.100.100.200",
            "[::1]",
            "metadata.google.internal",
        ],
    )
    async def test_blocked_literal_hosts(self, client, host):
        resp = await client.post(
            "/api/v1/webhooks",
            json={"url": f"http://{host}/hook", "events": ["invoice.paid"]},
            headers=AUTH,
        )
        assert resp.status_code == 422, f"Host {host} deveria ser bloqueado"


# --- RFC 1918 + private IP ranges ---


class TestSSRFPrivateIPs:
    """IPs privados (RFC 1918, link-local, etc.) devem ser bloqueados."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "ip",
        [
            "10.0.0.1",
            "10.255.255.255",
            "172.16.0.1",
            "172.31.255.255",
            "192.168.0.1",
            "192.168.1.100",
        ],
    )
    async def test_rfc1918_blocked(self, client, ip):
        resp = await client.post(
            "/api/v1/webhooks",
            json={"url": f"http://{ip}/hook", "events": ["invoice.paid"]},
            headers=AUTH,
        )
        assert resp.status_code == 422, f"IP {ip} (RFC 1918) deveria ser bloqueado"


# --- IPv6 private ---


class TestSSRFIPv6:
    """Enderecos IPv6 privados devem ser bloqueados."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "host",
        [
            "[::1]",        # loopback
            "[fc00::1]",    # ULA
            "[fe80::1]",    # link-local
        ],
    )
    async def test_ipv6_private_blocked(self, client, host):
        resp = await client.post(
            "/api/v1/webhooks",
            json={"url": f"http://{host}/hook", "events": ["invoice.paid"]},
            headers=AUTH,
        )
        assert resp.status_code == 422, f"IPv6 {host} deveria ser bloqueado"


# --- Bypass attempts ---


class TestSSRFBypassAttempts:
    """Tentativas de bypass por encoding alternativo devem ser bloqueadas."""

    @pytest.mark.asyncio
    async def test_octal_bypass(self, client):
        """0177.0.0.1 = 127.0.0.1 em octal."""
        resp = await client.post(
            "/api/v1/webhooks",
            json={"url": "http://0177.0.0.1/hook", "events": ["invoice.paid"]},
            headers=AUTH,
        )
        assert resp.status_code == 422, "Octal 0177.0.0.1 deveria ser bloqueado"

    @pytest.mark.asyncio
    async def test_decimal_bypass(self, client):
        """2130706433 = 127.0.0.1 em decimal."""
        resp = await client.post(
            "/api/v1/webhooks",
            json={"url": "http://2130706433/hook", "events": ["invoice.paid"]},
            headers=AUTH,
        )
        assert resp.status_code == 422, "Decimal 2130706433 deveria ser bloqueado"

    @pytest.mark.asyncio
    async def test_hex_bypass(self, client):
        """0x7f000001 = 127.0.0.1 em hex."""
        resp = await client.post(
            "/api/v1/webhooks",
            json={"url": "http://0x7f000001/hook", "events": ["invoice.paid"]},
            headers=AUTH,
        )
        assert resp.status_code == 422, "Hex 0x7f000001 deveria ser bloqueado"

    @pytest.mark.asyncio
    async def test_octal_10_network(self, client):
        """012.0.0.1 = 10.0.0.1 em octal."""
        resp = await client.post(
            "/api/v1/webhooks",
            json={"url": "http://012.0.0.1/hook", "events": ["invoice.paid"]},
            headers=AUTH,
        )
        assert resp.status_code == 422, "Octal 012.0.0.1 deveria ser bloqueado"


# --- DNS rebinding (resolve_and_check_url) ---


class TestSSRFDNSRebinding:
    """Hostnames que resolvem para IPs internos devem ser bloqueados no endpoint."""

    @pytest.mark.asyncio
    async def test_dns_resolves_to_private_ip(self, client):
        """Hostname que resolve para 10.0.0.1 deve ser bloqueado."""
        fake_addrinfo = [
            (2, 1, 6, "", ("10.0.0.1", 0)),  # AF_INET, SOCK_STREAM
        ]
        with patch("app.routers.webhooks.socket.getaddrinfo", return_value=fake_addrinfo):
            resp = await client.post(
                "/api/v1/webhooks",
                json={"url": "https://evil-rebind.example.com/hook", "events": ["invoice.paid"]},
                headers=AUTH,
            )
        assert resp.status_code == 422, "DNS rebinding para IP privado deveria ser bloqueado"

    @pytest.mark.asyncio
    async def test_dns_resolves_to_loopback(self, client):
        """Hostname que resolve para 127.0.0.1 deve ser bloqueado."""
        fake_addrinfo = [
            (2, 1, 6, "", ("127.0.0.1", 0)),
        ]
        with patch("app.routers.webhooks.socket.getaddrinfo", return_value=fake_addrinfo):
            resp = await client.post(
                "/api/v1/webhooks",
                json={"url": "https://sneaky.example.com/hook", "events": ["invoice.paid"]},
                headers=AUTH,
            )
        assert resp.status_code == 422, "DNS rebinding para loopback deveria ser bloqueado"

    @pytest.mark.asyncio
    async def test_dns_resolves_to_metadata(self, client):
        """Hostname que resolve para 169.254.169.254 deve ser bloqueado."""
        fake_addrinfo = [
            (2, 1, 6, "", ("169.254.169.254", 0)),
        ]
        with patch("app.routers.webhooks.socket.getaddrinfo", return_value=fake_addrinfo):
            resp = await client.post(
                "/api/v1/webhooks",
                json={"url": "https://metadata-steal.example.com/hook", "events": ["*"]},
                headers=AUTH,
            )
        assert resp.status_code == 422, "DNS rebinding para metadata deveria ser bloqueado"


# --- URLs validas ---


class TestSSRFValidURLs:
    """URLs publicas validas devem ser aceitas normalmente."""

    @pytest.mark.asyncio
    async def test_valid_https_url(self, client):
        with patch("app.routers.webhooks.socket.getaddrinfo") as mock_dns:
            mock_dns.return_value = [(2, 1, 6, "", ("93.184.216.34", 0))]
            resp = await client.post(
                "/api/v1/webhooks",
                json={"url": "https://example.com/hook", "events": ["invoice.paid"]},
                headers=AUTH,
            )
        assert resp.status_code == 201

    @pytest.mark.asyncio
    async def test_valid_http_url(self, client):
        with patch("app.routers.webhooks.socket.getaddrinfo") as mock_dns:
            mock_dns.return_value = [(2, 1, 6, "", ("93.184.216.34", 0))]
            resp = await client.post(
                "/api/v1/webhooks",
                json={"url": "http://webhook.example.org/events", "events": ["*"]},
                headers=AUTH,
            )
        assert resp.status_code == 201

    @pytest.mark.asyncio
    async def test_valid_url_with_port(self, client):
        with patch("app.routers.webhooks.socket.getaddrinfo") as mock_dns:
            mock_dns.return_value = [(2, 1, 6, "", ("93.184.216.34", 0))]
            resp = await client.post(
                "/api/v1/webhooks",
                json={"url": "https://hooks.example.com:8443/v1/receive", "events": ["invoice.paid"]},
                headers=AUTH,
            )
        assert resp.status_code == 201

    @pytest.mark.asyncio
    async def test_dns_failure_allows_through(self, client):
        """Se DNS nao resolve, deixa passar (vai falhar na entrega)."""
        import socket as _socket

        with patch("app.routers.webhooks.socket.getaddrinfo", side_effect=_socket.gaierror("nxdomain")):
            resp = await client.post(
                "/api/v1/webhooks",
                json={"url": "https://unknown-host.example.com/hook", "events": ["invoice.paid"]},
                headers=AUTH,
            )
        assert resp.status_code == 201


# --- Unit tests para _is_blocked_ip e _parse_ip_liberal ---


class TestIsBlockedIPUnit:
    """Testes unitarios para a funcao _is_blocked_ip."""

    def test_loopback_v4(self):
        from app.routers.webhooks import _is_blocked_ip
        assert _is_blocked_ip("127.0.0.1") is True

    def test_loopback_v6(self):
        from app.routers.webhooks import _is_blocked_ip
        assert _is_blocked_ip("::1") is True

    def test_rfc1918_10(self):
        from app.routers.webhooks import _is_blocked_ip
        assert _is_blocked_ip("10.0.0.1") is True

    def test_rfc1918_172(self):
        from app.routers.webhooks import _is_blocked_ip
        assert _is_blocked_ip("172.16.0.1") is True

    def test_rfc1918_192(self):
        from app.routers.webhooks import _is_blocked_ip
        assert _is_blocked_ip("192.168.1.1") is True

    def test_link_local(self):
        from app.routers.webhooks import _is_blocked_ip
        assert _is_blocked_ip("169.254.169.254") is True

    def test_ipv6_ula(self):
        from app.routers.webhooks import _is_blocked_ip
        assert _is_blocked_ip("fc00::1") is True

    def test_ipv6_link_local(self):
        from app.routers.webhooks import _is_blocked_ip
        assert _is_blocked_ip("fe80::1") is True

    def test_public_ip_allowed(self):
        from app.routers.webhooks import _is_blocked_ip
        assert _is_blocked_ip("8.8.8.8") is False

    def test_public_ip_allowed_2(self):
        from app.routers.webhooks import _is_blocked_ip
        assert _is_blocked_ip("93.184.216.34") is False

    def test_not_an_ip(self):
        from app.routers.webhooks import _is_blocked_ip
        assert _is_blocked_ip("example.com") is False

    def test_octal_loopback(self):
        from app.routers.webhooks import _is_blocked_ip
        assert _is_blocked_ip("0177.0.0.1") is True

    def test_decimal_loopback(self):
        from app.routers.webhooks import _is_blocked_ip
        assert _is_blocked_ip("2130706433") is True

    def test_hex_loopback(self):
        from app.routers.webhooks import _is_blocked_ip
        assert _is_blocked_ip("0x7f000001") is True
