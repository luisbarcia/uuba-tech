"""Router de gerenciamento de webhooks."""

import ipaddress
import json
import socket
from urllib.parse import urlparse

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.api_key import verify_api_key
from app.database import get_db
from app.exceptions import APIError
from app.models.webhook import Webhook
from app.utils.ids import generate_id

router = APIRouter(
    prefix="/api/v1/webhooks",
    tags=["webhooks"],
    dependencies=[Depends(verify_api_key)],
)


# Hostnames literais bloqueados (sem depender de resolucao DNS)
_BLOCKED_HOSTS = {
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
    "169.254.169.254",  # AWS/GCP metadata
    "100.100.100.200",  # Alibaba Cloud metadata
    "[::1]",
    "metadata.google.internal",
}


def _parse_ip_liberal(ip_str: str) -> ipaddress.IPv4Address | ipaddress.IPv6Address | None:
    """Tenta parsear IP em formatos alternativos que ipaddress nao aceita nativamente.

    Suporta:
    - Formato padrao: 127.0.0.1, ::1
    - Decimal inteiro: 2130706433 (= 127.0.0.1)
    - Hex inteiro: 0x7f000001 (= 127.0.0.1)
    - Octal por octeto: 0177.0.0.1 (= 127.0.0.1)
    """
    # Tentar parse direto (cobre IPv4/IPv6 normais)
    try:
        return ipaddress.ip_address(ip_str)
    except ValueError:
        pass

    # Tentar como inteiro decimal ou hex (ex: "2130706433", "0x7f000001")
    try:
        as_int = int(ip_str, 0)  # base 0 aceita 0x prefix
        if 0 <= as_int <= 0xFFFFFFFF:
            return ipaddress.IPv4Address(as_int)
    except (ValueError, OverflowError):
        pass

    # Tentar octal por octeto (ex: "0177.0.0.1")
    parts = ip_str.split(".")
    if len(parts) == 4:
        try:
            octets = [int(p, 8) if p.startswith("0") and len(p) > 1 else int(p, 10) for p in parts]
            if all(0 <= o <= 255 for o in octets):
                packed = (octets[0] << 24) | (octets[1] << 16) | (octets[2] << 8) | octets[3]
                return ipaddress.IPv4Address(packed)
        except (ValueError, OverflowError):
            pass

    return None


def _is_blocked_ip(ip_str: str) -> bool:
    """Checa se um IP (v4 ou v6) eh privado, reservado, loopback ou link-local.

    Aceita formatos alternativos: octal, decimal inteiro, hex.
    """
    addr = _parse_ip_liberal(ip_str)
    if addr is None:
        return False
    return (
        addr.is_private
        or addr.is_reserved
        or addr.is_loopback
        or addr.is_link_local
        or addr.is_multicast
    )


async def resolve_and_check_url(url: str) -> None:
    """Resolve hostname via DNS e checa se o IP resultante eh interno.

    Deve ser chamada no endpoint (async context), NAO no field_validator.
    Levanta APIError 422 se o IP resolvido for privado/reservado.
    """
    parsed = urlparse(url)
    hostname = parsed.hostname
    if not hostname:
        return

    try:
        # getaddrinfo eh sync mas rapido para DNS local; aceitavel aqui
        infos = socket.getaddrinfo(hostname, None, socket.AF_UNSPEC, socket.SOCK_STREAM)
    except socket.gaierror:
        # DNS nao resolveu — deixa passar (vai falhar no delivery)
        return

    for family, _type, _proto, _canonname, sockaddr in infos:
        ip_str = sockaddr[0]
        if _is_blocked_ip(ip_str):
            raise APIError(
                422,
                "url-bloqueada",
                "URL aponta para host interno bloqueado",
                f"O hostname '{hostname}' resolve para IP interno ({ip_str})",
            )


class WebhookCreate(BaseModel):
    url: str = Field(..., max_length=500, pattern=r"^https?://")
    events: list[str] = Field(..., min_length=1)

    @field_validator("url")
    @classmethod
    def _validate_url(cls, url: str) -> str:
        parsed = urlparse(url)
        hostname = parsed.hostname or ""

        # 1. Checagem por hostname literal
        if hostname in _BLOCKED_HOSTS:
            raise ValueError("URL aponta para host interno bloqueado")

        # 2. Tentar parsear hostname como IP (captura octal, hex, decimal)
        #    Strip brackets para IPv6: "[::1]" -> "::1"
        raw_host = hostname.strip("[]")
        if raw_host and _is_blocked_ip(raw_host):
            raise ValueError("URL aponta para host interno bloqueado")

        # 3. Validar scheme
        if parsed.scheme not in ("http", "https"):
            raise ValueError("URL deve usar http ou https")
        return url


def _to_response(w: Webhook) -> dict:
    return {
        "id": w.id,
        "url": w.url,
        "events": json.loads(w.events) if w.events else [],
        "active": w.active,
        "created_at": w.created_at.isoformat() if w.created_at else "",
    }


@router.get(
    "",
    summary="Listar webhooks",
    description="Lista webhooks registrados para o tenant.",
)
async def list_webhooks(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    tenant_id = request.state.tenant_id
    result = await db.execute(
        select(Webhook).where(Webhook.tenant_id == tenant_id).order_by(Webhook.created_at.desc())
    )
    return [_to_response(w) for w in result.scalars().all()]


@router.post(
    "",
    summary="Criar webhook",
    description="Registra um novo webhook para receber eventos.",
    status_code=201,
)
async def create_webhook(
    request: Request,
    data: WebhookCreate,
    db: AsyncSession = Depends(get_db),
):
    # DNS rebinding check — resolve hostname e verifica se IP eh interno
    await resolve_and_check_url(data.url)

    tenant_id = request.state.tenant_id
    webhook = Webhook(
        id=generate_id("whk"),
        tenant_id=tenant_id,
        url=data.url,
        events=json.dumps(data.events),
        active=True,
    )
    db.add(webhook)
    await db.commit()
    await db.refresh(webhook)
    return _to_response(webhook)


@router.post(
    "/{webhook_id}/test",
    summary="Testar webhook",
    description="Envia evento de teste para o webhook.",
)
async def test_webhook(
    request: Request,
    webhook_id: str,
    db: AsyncSession = Depends(get_db),
):
    tenant_id = request.state.tenant_id
    result = await db.execute(
        select(Webhook).where(and_(Webhook.id == webhook_id, Webhook.tenant_id == tenant_id))
    )
    webhook = result.scalar_one_or_none()
    if not webhook:
        raise APIError(404, "webhook-nao-encontrado", "Webhook nao encontrado", f"ID: {webhook_id}")
    return {"status": "ok", "message": f"Teste enviado para {webhook.url}"}


@router.delete(
    "/{webhook_id}",
    summary="Remover webhook",
    description="Remove um webhook registrado.",
    status_code=204,
)
async def delete_webhook(
    request: Request,
    webhook_id: str,
    db: AsyncSession = Depends(get_db),
):
    tenant_id = request.state.tenant_id
    result = await db.execute(
        select(Webhook).where(and_(Webhook.id == webhook_id, Webhook.tenant_id == tenant_id))
    )
    webhook = result.scalar_one_or_none()
    if not webhook:
        raise APIError(404, "webhook-nao-encontrado", "Webhook nao encontrado", f"ID: {webhook_id}")
    await db.delete(webhook)
    await db.commit()
