from fastapi import Security
from fastapi.security import APIKeyHeader
from app.config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str | None = Security(api_key_header)) -> str:
    import hmac as _hmac

    if not api_key or not _hmac.compare_digest(api_key, settings.api_key):
        from app.exceptions import APIError

        raise APIError(401, "auth-invalida", "Autenticação inválida", "API key ausente ou inválida")
    return api_key
