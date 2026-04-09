"""Idempotency helpers — dedup POST requests via Idempotency-Key header."""

import hashlib
import json
import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import APIError
from app.models.idempotency import IdempotencyCache

logger = logging.getLogger("uuba")

IDEMPOTENCY_TTL = timedelta(hours=24)


def hash_body(body: bytes) -> str:
    """SHA-256 hex hash do request body."""
    return hashlib.sha256(body).hexdigest()


async def check_idempotency(
    db: AsyncSession,
    tenant_id: str,
    idempotency_key: str,
    body: bytes,
) -> IdempotencyCache | None:
    """Verifica cache. Retorna entry se hit, None se miss. Raises 422 se mismatch."""
    cache_key = f"{tenant_id}:{idempotency_key}"
    body_hash = hash_body(body)

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
        body_hash=hash_body(body),
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
