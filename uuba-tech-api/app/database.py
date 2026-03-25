from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from app.config import settings
from app.infrastructure.event_bus import InMemoryEventBus

engine = create_async_engine(settings.database_url, echo=settings.debug)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Singleton EventBus — substituído por PgNotifyEventBus em DP-09
_event_bus = InMemoryEventBus()


async def get_db():
    """Dependency injection de AsyncSession para endpoints FastAPI.

    Yields:
        AsyncSession: Sessão assíncrona do SQLAlchemy, fechada automaticamente ao fim do request.
    """
    async with async_session() as session:
        yield session


# --- Repository Factories (DP-04) ---


async def get_fatura_repository():
    """DI factory para FaturaRepository."""
    from app.infrastructure.repositories.sqlalchemy_fatura_repo import SqlAlchemyFaturaRepository

    async with async_session() as session:
        yield SqlAlchemyFaturaRepository(session)


async def get_cobranca_repository():
    """DI factory para CobrancaRepository."""
    from app.infrastructure.repositories.sqlalchemy_cobranca_repo import (
        SqlAlchemyCobrancaRepository,
    )

    async with async_session() as session:
        yield SqlAlchemyCobrancaRepository(session)


async def get_cliente_repository():
    """DI factory para ClienteRepository."""
    from app.infrastructure.repositories.sqlalchemy_cliente_repo import SqlAlchemyClienteRepository

    async with async_session() as session:
        yield SqlAlchemyClienteRepository(session)


def get_event_bus() -> InMemoryEventBus:
    """DI factory para EventBus (DP-03). Retorna singleton."""
    return _event_bus
