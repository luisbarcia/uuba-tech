"""InMemoryEventBus — implementação em memória para testes e uso inicial.

PG NOTIFY será implementado em DP-09 (Observer Pattern).
"""

from __future__ import annotations

from collections import defaultdict

from app.domain.events.base import DomainEvent
from app.domain.events.event_bus import EventHandler


class InMemoryEventBus:
    """EventBus em memória — publish/subscribe síncrono por tipo de evento."""

    def __init__(self) -> None:
        self._handlers: dict[type[DomainEvent], list[EventHandler]] = defaultdict(list)

    def subscribe(
        self,
        event_type: type[DomainEvent],
        handler: EventHandler,
    ) -> None:
        self._handlers[event_type].append(handler)

    async def publish(self, event: DomainEvent) -> None:
        for handler in self._handlers.get(type(event), []):
            await handler(event)

    async def publish_all(self, events: list[DomainEvent]) -> None:
        for event in events:
            await self.publish(event)
