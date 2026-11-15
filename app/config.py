from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://next_offer:change_me@localhost:5432/next_offer"
    rabbitmq_url: str = "amqp://next_offer:change_me@localhost:5672/"
    uvicorn_host: str = "0.0.0.0"
    uvicorn_port: int = 8000
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    llm_enabled: bool = False
    yandex_api_key: str = ""
    yandex_folder_id: str = ""
    yandex_model: str = "yandexgpt-lite"
    yandex_model_version: str = "latest"
    yandex_model_uri: str = ""
    yandex_timeout_seconds: float = 10.0
    yandex_temperature: float = 0.7
    yandex_max_tokens: int = 200

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def yandex_resolved_model_uri(self) -> str:
        if self.yandex_model_uri:
            return self.yandex_model_uri
        return f"gpt://{self.yandex_folder_id}/{self.yandex_model}/{self.yandex_model_version}"


settings = Settings()
