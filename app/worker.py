import logging
import time

import pika

from app.config import settings

logger = logging.getLogger(__name__)

EVENTS_QUEUE = "next_offer.events"
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
        logger.info("Waiting for events on queue %s", EVENTS_QUEUE)
        while True:
            connection.process_data_events(time_limit=1)
    except KeyboardInterrupt:
        logger.info("Worker stopping")
    finally:
        if connection.is_open:
            connection.close()


if __name__ == "__main__":
    main()
