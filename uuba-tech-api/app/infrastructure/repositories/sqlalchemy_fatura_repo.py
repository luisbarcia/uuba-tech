"""Implementação SQLAlchemy do FaturaRepository (multi-tenant)."""

import logging
from datetime import datetime, timezone

from sqlalchemy import exists, func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.value_objects.fatura_status import FaturaStatus
from app.exceptions import APIError
from app.models.fatura import Fatura

logger = logging.getLogger("uuba")


class SqlAlchemyFaturaRepository:
    """Repositório de Faturas via SQLAlchemy AsyncSession — filtrado por tenant."""

    def __init__(self, session: AsyncSession, tenant_id: str) -> None:
        self._session = session
        self._tenant_id = tenant_id

    async def get_by_id(self, fatura_id: str) -> Fatura | None:
        result = await self._session.execute(
            select(Fatura).where(
                Fatura.id == fatura_id,
                Fatura.tenant_id == self._tenant_id,
            )
        )
        return result.scalar_one_or_none()

    async def create(self, fatura: Fatura) -> Fatura:
        fatura.tenant_id = self._tenant_id
        self._session.add(fatura)
        try:
            await self._session.commit()
        except IntegrityError:
            await self._session.rollback()
            raise APIError(
                409,
                "integridade",
                "Erro de integridade",
                f"Cliente {fatura.cliente_id} não existe ou violação de constraint.",
            )
        await self._session.refresh(fatura)
        return fatura

    async def update(self, fatura: Fatura) -> Fatura:
        await self._session.commit()
        await self._session.refresh(fatura)
        return fatura

    async def list_by_filters(
        self,
        *,
        status: str | None = None,
        cliente_id: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[Fatura], int]:
        base = Fatura.tenant_id == self._tenant_id
        query = select(Fatura).where(base)
        count_q = select(func.count(Fatura.id)).where(base)

        if status:
            statuses = [s.strip() for s in status.split(",")]
            query = query.where(Fatura.status.in_(statuses))
            count_q = count_q.where(Fatura.status.in_(statuses))
        if cliente_id:
            query = query.where(Fatura.cliente_id == cliente_id)
            count_q = count_q.where(Fatura.cliente_id == cliente_id)

        total = (await self._session.execute(count_q)).scalar() or 0
        result = await self._session.execute(
            query.order_by(Fatura.vencimento).limit(limit).offset(offset)
        )
        return result.scalars().all(), total

    async def bulk_transicionar_vencidas(self) -> int:
        now = datetime.now(timezone.utc)
        stmt = (
            update(Fatura)
            .where(
                Fatura.tenant_id == self._tenant_id,
                Fatura.status == FaturaStatus.PENDENTE.value,
                Fatura.vencimento < now,
            )
            .values(status=FaturaStatus.VENCIDO.value, updated_at=now)
        )
        result = await self._session.execute(stmt)
        await self._session.commit()
        count = result.rowcount
        logger.info(f"transicionar_faturas_vencidas: {count} fatura(s) pendente→vencido")
        return count

    async def exists_by_numero_nf_and_cliente(self, numero_nf: str, cliente_id: str) -> bool:
        stmt = select(
            exists().where(
                Fatura.numero_nf == numero_nf,
                Fatura.cliente_id == cliente_id,
                Fatura.tenant_id == self._tenant_id,
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar() or False
