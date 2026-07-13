from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://studio:studio@localhost:5432/studio"
    redis_url: str = "redis://localhost:6379/0"
    file_storage_dir: str = "./storage"
    model_provider: str = "openai_compatible"
    model_base_url: str = "https://api.openai.com/v1"
    model_api_key: str = ""
    chat_model: str = "gpt-4.1-mini"
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
