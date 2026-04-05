"""Router de gerenciamento de webhooks."""

import json

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


_BLOCKED_HOSTS = {"localhost", "127.0.0.1", "0.0.0.0", "169.254.169.254", "[::1]"}


class WebhookCreate(BaseModel):
    url: str = Field(..., max_length=500, pattern=r"^https?://")
    events: list[str] = Field(..., min_length=1)

    @field_validator("url")
    @classmethod
    def _validate_url(cls, url: str) -> str:
        from urllib.parse import urlparse

        parsed = urlparse(url)
        if parsed.hostname and parsed.hostname in _BLOCKED_HOSTS:
            raise ValueError("URL aponta para host interno bloqueado")
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
