"""Implementação SQLAlchemy do ClienteRepository."""

import hashlib
from datetime import datetime, timezone

from sqlalchemy import select, func, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import APIError
from app.models.cliente import Cliente
from app.models.cobranca import Cobranca


class SqlAlchemyClienteRepository:
    """Repositório de Clientes via SQLAlchemy AsyncSession."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, cliente_id: str) -> Cliente | None:
        result = await self._session.execute(
            select(Cliente).where(
                Cliente.id == cliente_id,
                Cliente.deletado_em.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_documento(self, documento: str) -> Cliente | None:
        result = await self._session.execute(
            select(Cliente).where(
                Cliente.documento == documento,
                Cliente.deletado_em.is_(None),
            )
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
        base = Cliente.deletado_em.is_(None)
        query = select(Cliente).where(base)
        count_q = select(func.count(Cliente.id)).where(base)

        if telefone:
            query = query.where(Cliente.telefone == telefone)
            count_q = count_q.where(Cliente.telefone == telefone)

        total = (await self._session.execute(count_q)).scalar() or 0
        result = await self._session.execute(
            query.order_by(Cliente.nome).limit(limit).offset(offset)
        )
        return result.scalars().all(), total

    async def anonimizar(self, cliente_id: str) -> bool:
        """Anonimiza PII do cliente (LGPD Art. 18 VI)."""
        result = await self._session.execute(
            select(Cliente).where(
                Cliente.id == cliente_id,
                Cliente.deletado_em.is_(None),
            )
        )
        cliente = result.scalar_one_or_none()
        if not cliente:
            return False

        doc_hash = hashlib.sha256(cliente.documento.encode()).hexdigest()[:14]
        cliente.nome = "REMOVIDO"
        cliente.documento = doc_hash
        cliente.email = None
        cliente.telefone = None
        cliente.deletado_em = datetime.now(timezone.utc)
        await self._session.commit()
        return True

    async def anonimizar_mensagens(self, cliente_id: str) -> int:
        """Remove mensagens de cobrança do cliente (LGPD)."""
        result = await self._session.execute(
            update(Cobranca).where(Cobranca.cliente_id == cliente_id).values(mensagem=None)
        )
        await self._session.commit()
        return result.rowcount
