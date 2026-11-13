from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://rozochka:rozochka@localhost:5432/rozochka"
    rabbitmq_url: str = "amqp://nextoffer:nextoffer@localhost:5672/"
    uvicorn_host: str = "0.0.0.0"
    uvicorn_port: int = 8000

    class Config:
        env_file = ".env"


settings = Settings()
