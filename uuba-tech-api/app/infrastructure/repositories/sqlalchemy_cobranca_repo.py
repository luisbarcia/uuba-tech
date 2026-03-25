"""Implementação SQLAlchemy do CobrancaRepository (multi-tenant)."""

import re
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import APIError
from app.models.cobranca import Cobranca


class SqlAlchemyCobrancaRepository:
    """Repositório de Cobranças via SQLAlchemy AsyncSession — filtrado por tenant."""

    def __init__(self, session: AsyncSession, tenant_id: str) -> None:
        self._session = session
        self._tenant_id = tenant_id

    async def get_by_id(self, cobranca_id: str) -> Cobranca | None:
        result = await self._session.execute(
            select(Cobranca).where(
                Cobranca.id == cobranca_id,
                Cobranca.tenant_id == self._tenant_id,
            )
        )
        return result.scalar_one_or_none()

    async def create(self, cobranca: Cobranca) -> Cobranca:
        cobranca.tenant_id = self._tenant_id
        self._session.add(cobranca)
        try:
            await self._session.commit()
        except IntegrityError:
            await self._session.rollback()
            raise APIError(
                409,
                "integridade",
                "Erro de integridade",
                f"Fatura {cobranca.fatura_id} ou cliente {cobranca.cliente_id} não existe.",
            )
        await self._session.refresh(cobranca)
        return cobranca

    async def update(self, cobranca: Cobranca) -> Cobranca:
        await self._session.commit()
        await self._session.refresh(cobranca)
        return cobranca

    async def list_by_filters(
        self,
        *,
        periodo: str | None = None,
        cliente_id: str | None = None,
        fatura_id: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[Cobranca], int]:
        base = Cobranca.tenant_id == self._tenant_id
        query = select(Cobranca).where(base)
        count_q = select(func.count(Cobranca.id)).where(base)

        if periodo:
            match = re.fullmatch(r"(\d+)d", periodo)
            if not match:
                raise APIError(
                    422,
                    "periodo-invalido",
                    "Formato de período inválido",
                    f"Use o formato Nd (ex: 7d, 30d). Recebido: '{periodo}'.",
                )
            days = int(match.group(1))
            since = datetime.now(timezone.utc) - timedelta(days=days)
            query = query.where(Cobranca.created_at >= since)
            count_q = count_q.where(Cobranca.created_at >= since)

        if cliente_id:
            query = query.where(Cobranca.cliente_id == cliente_id)
            count_q = count_q.where(Cobranca.cliente_id == cliente_id)
        if fatura_id:
            query = query.where(Cobranca.fatura_id == fatura_id)
            count_q = count_q.where(Cobranca.fatura_id == fatura_id)

        total = (await self._session.execute(count_q)).scalar() or 0
        result = await self._session.execute(
            query.order_by(Cobranca.created_at.desc()).limit(limit).offset(offset)
        )
        return result.scalars().all(), total

    async def list_by_fatura(self, fatura_id: str) -> list[Cobranca]:
        result = await self._session.execute(
            select(Cobranca)
            .where(
                Cobranca.fatura_id == fatura_id,
                Cobranca.tenant_id == self._tenant_id,
            )
            .order_by(Cobranca.created_at.desc())
        )
        return result.scalars().all()
