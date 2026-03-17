from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://uuba:uuba@localhost:5432/uuba"
    api_key: str = "uuba-dev-key-change-me"
    asaas_webhook_secret: str = ""
    whatsapp_verify_token: str = ""
    environment: str = "development"
    debug: bool = False

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
