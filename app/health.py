import logging

import pika
from sqlalchemy import text

from app.config import settings
from app.db import get_engine

logger = logging.getLogger(__name__)

RABBITMQ_TIMEOUT_SECONDS = 1.0


def check_database() -> bool:
    try:
        with get_engine().connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception as error:
        logger.warning("Database health check failed: %s", error)
        return False
    return True


def check_rabbitmq(url: str | None = None) -> bool:
    try:
        parameters = pika.URLParameters(url or settings.rabbitmq_url)
        parameters.socket_timeout = RABBITMQ_TIMEOUT_SECONDS
        parameters.stack_timeout = RABBITMQ_TIMEOUT_SECONDS
        connection = pika.BlockingConnection(parameters)
        connection.close()
    except Exception as error:
        logger.warning("RabbitMQ health check failed: %s", error)
        return False
    return True


def collect_health() -> dict:
    checks = {
        "database": "ok" if check_database() else "error",
        "rabbitmq": "ok" if check_rabbitmq() else "error",
    }
    healthy = all(result == "ok" for result in checks.values())
    return {
        "status": "ok" if healthy else "degraded",
        "checks": checks,
    }
