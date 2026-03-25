"""Protocol interface para repositório de Clientes."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from app.models.cliente import Cliente


@runtime_checkable
class ClienteRepository(Protocol):
    """Interface de repositório para persistência de Clientes."""

    async def get_by_id(self, cliente_id: str) -> Cliente | None:
        """Busca cliente por ID."""
        ...

    async def get_by_documento(self, documento: str) -> Cliente | None:
        """Busca cliente por documento (CPF/CNPJ)."""
        ...

    async def create(self, cliente: Cliente) -> Cliente:
        """Persiste novo cliente. Levanta IntegrityError se documento duplicado."""
        ...

    async def update(self, cliente: Cliente) -> Cliente:
        """Persiste alterações no cliente."""
        ...

    async def list_by_filters(
        self,
        *,
        telefone: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[Cliente], int]:
        """Lista clientes com filtros e paginação."""
        ...
