import json
from functools import lru_cache
from typing import Any, Protocol

import pika

from app.config import settings

EVENTS_QUEUE = "next_offer.events"


class EventPublisher(Protocol):
    def publish(self, message: dict[str, Any]) -> None: ...


class RabbitMQPublisher:
    def __init__(self, url: str, queue: str = EVENTS_QUEUE) -> None:
        self.url = url
        self.queue = queue

    def publish(self, message: dict[str, Any]) -> None:
        connection = pika.BlockingConnection(pika.URLParameters(self.url))
        try:
            channel = connection.channel()
            channel.queue_declare(queue=self.queue, durable=True)
            channel.basic_publish(
                exchange="",
                routing_key=self.queue,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    content_type="application/json",
                    delivery_mode=2,
                ),
            )
        finally:
            if connection.is_open:
                connection.close()


@lru_cache
def get_publisher() -> EventPublisher:
    return RabbitMQPublisher(settings.rabbitmq_url)
