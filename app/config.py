from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://rozochka:rozochka@localhost:5432/rozochka"
    rabbitmq_url: str = "amqp://nextoffer:nextoffer@localhost:5672/"
    uvicorn_host: str = "0.0.0.0"
    uvicorn_port: int = 8000
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
