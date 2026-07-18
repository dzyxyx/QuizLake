from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    #App
    project_name: str
    version: str = "0.1.0"
    environment: str
    debug: bool
    api_v1_prefix: str = "/api/v1"
    allowed_origins: list[str]

    #PostgreSQL
    postgres_host: str
    postgres_port: int
    postgres_db: str
    postgres_user: str
    postgres_password: str

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )
    
    @property
    def DATABASE_URL_SYNC(self):
        return (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    #JWT
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int

settings = Settings()