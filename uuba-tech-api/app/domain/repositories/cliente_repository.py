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
        """Lista clientes com filtros e paginação. Exclui deletados."""
        ...

    async def anonimizar(self, cliente_id: str) -> bool:
        """Anonimiza dados PII do cliente (LGPD Art. 18 VI).

        Retorna True se anonimizado, False se não encontrado.
        """
        ...

    async def anonimizar_mensagens(self, cliente_id: str) -> int:
        """Remove mensagens de cobrança do cliente (LGPD).

        Retorna quantidade de cobranças anonimizadas.
        """
        ...
