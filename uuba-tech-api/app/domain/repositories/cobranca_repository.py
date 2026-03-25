"""Protocol interface para repositório de Cobranças."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from app.models.cobranca import Cobranca


@runtime_checkable
class CobrancaRepository(Protocol):
    """Interface de repositório para persistência de Cobranças."""

    async def get_by_id(self, cobranca_id: str) -> Cobranca | None:
        """Busca cobrança por ID."""
        ...

    async def create(self, cobranca: Cobranca) -> Cobranca:
        """Persiste nova cobrança."""
        ...

    async def update(self, cobranca: Cobranca) -> Cobranca:
        """Persiste alterações na cobrança."""
        ...

    async def list_by_filters(
        self,
        *,
        periodo: str | None = None,
        cliente_id: str | None = None,
        fatura_id: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[Cobranca], int]:
        """Lista cobranças com filtros e paginação."""
        ...

    async def list_by_fatura(self, fatura_id: str) -> list[Cobranca]:
        """Retorna cobranças de uma fatura, ordenadas por created_at desc."""
        ...
