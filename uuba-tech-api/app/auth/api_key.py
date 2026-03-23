from fastapi import Security
from fastapi.security import APIKeyHeader
from app.config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str | None = Security(api_key_header)) -> str:
    """Valida a API key enviada no header ``X-API-Key``.

    Usa comparação constant-time (HMAC) para prevenir timing attacks.

    Args:
        api_key: Valor do header X-API-Key (injetado pelo FastAPI Security).

    Returns:
        A API key validada.

    Raises:
        APIError: 401 se a key for ausente ou inválida.
    """
    import hmac as _hmac

    if not api_key or not _hmac.compare_digest(api_key, settings.api_key):
        from app.exceptions import APIError

        raise APIError(401, "auth-invalida", "Autenticação inválida", "API key ausente ou inválida")
    return api_key
