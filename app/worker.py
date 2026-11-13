import json
import logging
import time
from typing import Any

import pika
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties

from app.config import settings
from app.db import get_session_factory
from app.messaging import EVENTS_QUEUE
from app.services.offers import handle_event

logger = logging.getLogger(__name__)

CONNECT_RETRY_DELAY_SECONDS = 2


def connect_with_retry(parameters: pika.URLParameters) -> pika.BlockingConnection:
    attempt = 0
    while True:
        attempt += 1
        try:
            connection = pika.BlockingConnection(parameters)
        except pika.exceptions.AMQPConnectionError:
            logger.warning(
                "RabbitMQ is not available (attempt %d), retrying in %ds",
                attempt,
                CONNECT_RETRY_DELAY_SECONDS,
            )
            time.sleep(CONNECT_RETRY_DELAY_SECONDS)
            continue

        logger.info("Worker connected to RabbitMQ at %s", settings.rabbitmq_url)
        return connection


def process_message(body: bytes) -> None:
    message: dict[str, Any] = json.loads(body)
    with get_session_factory()() as db:
        handle_event(message, db)


def on_message(
    channel: BlockingChannel,
    method: Basic.Deliver,
    properties: BasicProperties,
    body: bytes,
) -> None:
    try:
        process_message(body)
    except Exception:
        logger.exception("Failed to process event message: %s", body[:500])
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        return

    channel.basic_ack(delivery_tag=method.delivery_tag)


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    logger.info("Starting next_offer worker")

    connection = connect_with_retry(pika.URLParameters(settings.rabbitmq_url))
    try:
        channel = connection.channel()
        channel.queue_declare(queue=EVENTS_QUEUE, durable=True)
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(
            queue=EVENTS_QUEUE,
            on_message_callback=on_message,
        )
        logger.info("Waiting for events on queue %s", EVENTS_QUEUE)
        channel.start_consuming()
    except KeyboardInterrupt:
        logger.info("Worker stopping")
    finally:
        if connection.is_open:
            connection.close()


if __name__ == "__main__":
    main()
