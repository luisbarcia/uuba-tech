from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configurações da aplicação, carregadas de variáveis de ambiente ou ``.env``."""

    database_url: str = "postgresql+asyncpg://uuba:uuba@localhost:5432/uuba"
    api_key: str = "uuba-dev-key-change-me"  # DEVE ser alterado em producao via env var
    asaas_webhook_secret: str = ""
    whatsapp_verify_token: str = ""
    environment: str = "development"
    debug: bool = False
    uuba_encryption_key: str = ""  # AES-256-GCM key para cofre de credenciais

    # OAuth
    oauth_state_ttl_minutes: int = 60  # TTL do state token (link de autorizacao)

    # LGPD: Períodos de retenção (Art. 15/16)
    retencao_faturas_anos: int = 5
    retencao_mensagens_anos: int = 2
    retencao_clientes_inativos_anos: int = 5

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()

# Bloqueia producao com credenciais default
if settings.environment == "production":
    import os as _os

    if not _os.environ.get("UNKEY_ROOT_KEY"):
        raise RuntimeError(
            "FATAL: UNKEY_ROOT_KEY nao definido em producao. "
            "Autenticacao via Unkey requer root key."
        )
    if "uuba:uuba@" in settings.database_url:
        raise RuntimeError(
            "FATAL: DATABASE_URL com credenciais default em producao. "
            "Defina DATABASE_URL via env var."
        )
