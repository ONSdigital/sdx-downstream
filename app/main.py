import logging

from sdc.rabbit import MessageConsumer
from sdc.rabbit import QueuePublisher

from app.processors.message_processor import MessageProcessor
import app.settings


def run():
    logging.basicConfig(format=app.settings.LOGGING_FORMAT,
                        datefmt="%Y-%m-%dT%H:%M:%S",
                        level=app.settings.LOGGING_LEVEL)
    logging.getLogger('sdc.rabbit').setLevel(logging.INFO)

    message_processor = MessageProcessor()

    quarantine_publisher = QueuePublisher(
        urls=app.settings.RABBIT_URLS,
        queue=app.settings.RABBIT_QUARANTINE_QUEUE
    )

    message_consumer = MessageConsumer(
        durable_queue=True,
        exchange=app.settings.RABBIT_EXCHANGE,
        exchange_type='topic',
        rabbit_queue=app.settings.RABBIT_QUEUE,
        rabbit_urls=app.settings.RABBIT_URLS,
        quarantine_publisher=quarantine_publisher,
        process=message_processor.process
    )

    try:
        message_consumer.run()
    except KeyboardInterrupt:
        message_consumer.stop()


if __name__ == "__main__":
    run()
