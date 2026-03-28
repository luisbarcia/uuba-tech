"""Protocol interface para repositório de Faturas.

Define o contrato que qualquer implementação (SQLAlchemy, InMemory) deve seguir.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from app.models.fatura import Fatura


@runtime_checkable
class FaturaRepository(Protocol):
    """Interface de repositório para persistência de Faturas."""

    async def get_by_id(self, fatura_id: str) -> Fatura | None:
        """Busca fatura por ID."""
        ...

    async def create(self, fatura: Fatura) -> Fatura:
        """Persiste nova fatura. Levanta IntegrityError se FK inválida."""
        ...

    async def update(self, fatura: Fatura) -> Fatura:
        """Persiste alterações na fatura."""
        ...

    async def list_by_filters(
        self,
        *,
        status: str | None = None,
        cliente_id: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[Fatura], int]:
        """Lista faturas com filtros e paginação. Retorna (items, total)."""
        ...

    async def bulk_transicionar_vencidas(self) -> int:
        """Transiciona faturas pendentes vencidas para 'vencido'. Retorna contagem."""
        ...

    async def exists_by_numero_nf_and_cliente(self, numero_nf: str, cliente_id: str) -> bool:
        """Verifica se já existe fatura com numero_nf + cliente_id."""
        ...

    async def get_metricas_agregadas(self, cliente_id: str) -> dict:
        """Calcula metricas via SQL aggregation (sem carregar todas as linhas)."""
        ...
