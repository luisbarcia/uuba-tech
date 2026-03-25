from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configurações da aplicação, carregadas de variáveis de ambiente ou ``.env``."""

    database_url: str = "postgresql+asyncpg://uuba:uuba@localhost:5432/uuba"
    api_key: str = "uuba-dev-key-change-me"
    asaas_webhook_secret: str = ""
    whatsapp_verify_token: str = ""
    environment: str = "development"
    debug: bool = False

    # LGPD: Períodos de retenção (Art. 15/16)
    retencao_faturas_anos: int = 5
    retencao_mensagens_anos: int = 2
    retencao_clientes_inativos_anos: int = 5

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
