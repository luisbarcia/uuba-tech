"""Implementação SQLAlchemy do ClienteRepository."""

from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cliente import Cliente
from app.exceptions import APIError


class SqlAlchemyClienteRepository:
    """Repositório de Clientes via SQLAlchemy AsyncSession."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, cliente_id: str) -> Cliente | None:
        result = await self._session.execute(
            select(Cliente).where(Cliente.id == cliente_id)
        )
        return result.scalar_one_or_none()

    async def get_by_documento(self, documento: str) -> Cliente | None:
        result = await self._session.execute(
            select(Cliente).where(Cliente.documento == documento)
        )
        return result.scalar_one_or_none()

    async def create(self, cliente: Cliente) -> Cliente:
        self._session.add(cliente)
        try:
            await self._session.commit()
        except IntegrityError:
            await self._session.rollback()
            raise APIError(
                409,
                "documento-duplicado",
                "Documento já cadastrado",
                f"Já existe um cliente com o documento {cliente.documento}.",
            )
        await self._session.refresh(cliente)
        return cliente

    async def update(self, cliente: Cliente) -> Cliente:
        await self._session.commit()
        await self._session.refresh(cliente)
        return cliente

    async def list_by_filters(
        self,
        *,
        telefone: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[Cliente], int]:
        query = select(Cliente)
        count_q = select(func.count(Cliente.id))

        if telefone:
            query = query.where(Cliente.telefone == telefone)
            count_q = count_q.where(Cliente.telefone == telefone)

        total = (await self._session.execute(count_q)).scalar() or 0
        result = await self._session.execute(
            query.order_by(Cliente.nome).limit(limit).offset(offset)
        )
        return result.scalars().all(), total
