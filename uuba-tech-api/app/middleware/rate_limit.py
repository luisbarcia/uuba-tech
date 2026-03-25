"""Rate limiting middleware (LGPD Art. 46 — proteção contra extração em massa).

Implementação in-memory por API key. Para produção com múltiplas instâncias,
migrar para Redis. Desabilitado em testes via env TESTING=1.
"""

import os
import time
from collections import defaultdict

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

# Configuração: max requisições por janela de tempo
RATE_LIMIT = 100  # requisições
RATE_WINDOW = 60  # segundos


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Limita requisições por API key usando sliding window counter."""

    def __init__(self, app, rate_limit: int = RATE_LIMIT, window: int = RATE_WINDOW):
        super().__init__(app)
        self.rate_limit = rate_limit
        self.window = window
        self._requests: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        # Desabilitado em testes
        if os.environ.get("TESTING"):
            return await call_next(request)

        # Endpoints públicos não têm rate limit
        if request.url.path in ("/health", "/api/v1/privacidade"):
            return await call_next(request)

        key = request.headers.get("x-api-key", request.client.host if request.client else "unknown")
        now = time.time()

        # Limpar entradas antigas
        self._requests[key] = [t for t in self._requests[key] if t > now - self.window]

        if len(self._requests[key]) >= self.rate_limit:
            return JSONResponse(
                status_code=429,
                content={
                    "type": "rate-limit-exceeded",
                    "title": "Limite de requisições excedido",
                    "detail": f"Máximo de {self.rate_limit} requisições "
                    f"por {self.window}s. Tente novamente em instantes.",
                    "status": 429,
                },
            )

        self._requests[key].append(now)
        return await call_next(request)
