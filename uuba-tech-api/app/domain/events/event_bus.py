"""Protocol para EventBus — interface de domínio.

A implementação concreta (InMemoryEventBus, PgNotifyEventBus) fica
na camada de infraestrutura. O domínio só conhece este Protocol.
"""

from __future__ import annotations

from collections.abc import Callable, Coroutine
from typing import Any, Protocol, runtime_checkable

from app.domain.events.base import DomainEvent

EventHandler = Callable[[Any], Coroutine[Any, Any, None]]


@runtime_checkable
class EventBus(Protocol):
    """Interface para publicação e assinatura de domain events."""

    def subscribe(
        self,
        event_type: type[DomainEvent],
        handler: EventHandler,
    ) -> None: ...

    async def publish(self, event: DomainEvent) -> None: ...

    async def publish_all(self, events: list[DomainEvent]) -> None: ...
