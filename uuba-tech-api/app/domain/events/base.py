"""Classe base para Domain Events.

Domain Events são fatos imutáveis que aconteceram no domínio.
Nomeados sempre no passado: FaturaVenceu, PagamentoConfirmado.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.utils.ids import generate_id


@dataclass(frozen=True)
class DomainEvent:
    """Classe base para todos os eventos de domínio.

    Attributes:
        event_id: Identificador único do evento (prefixo evt_).
        occurred_at: Timestamp UTC de quando o evento ocorreu.
    """

    event_id: str = field(default_factory=lambda: generate_id("evt"))
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
