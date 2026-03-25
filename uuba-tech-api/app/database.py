from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.infrastructure.event_bus import InMemoryEventBus

engine = create_async_engine(settings.database_url, echo=settings.debug)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Singleton EventBus — substituído por PgNotifyEventBus em DP-09
_event_bus = InMemoryEventBus()


async def get_db():
    """Dependency injection de AsyncSession para endpoints FastAPI."""
    async with async_session() as session:
        yield session


def _get_tenant_id(request: Request) -> str:
    """Extrai tenant_id do request (injetado pelo verify_api_key)."""
    return request.state.tenant_id


# --- Repository Factories (DP-04, multi-tenant) ---


async def get_fatura_repository(request: Request):
    """DI factory para FaturaRepository — filtrado por tenant."""
    from app.infrastructure.repositories.sqlalchemy_fatura_repo import SqlAlchemyFaturaRepository

    tenant_id = _get_tenant_id(request)
    async with async_session() as session:
        yield SqlAlchemyFaturaRepository(session, tenant_id)


async def get_cobranca_repository(request: Request):
    """DI factory para CobrancaRepository — filtrado por tenant."""
    from app.infrastructure.repositories.sqlalchemy_cobranca_repo import (
        SqlAlchemyCobrancaRepository,
    )

    tenant_id = _get_tenant_id(request)
    async with async_session() as session:
        yield SqlAlchemyCobrancaRepository(session, tenant_id)


async def get_cliente_repository(request: Request):
    """DI factory para ClienteRepository — filtrado por tenant."""
    from app.infrastructure.repositories.sqlalchemy_cliente_repo import SqlAlchemyClienteRepository

    tenant_id = _get_tenant_id(request)
    async with async_session() as session:
        yield SqlAlchemyClienteRepository(session, tenant_id)


def get_event_bus() -> InMemoryEventBus:
    """DI factory para EventBus (DP-03). Retorna singleton."""
    return _event_bus
