import logging
import structlog
from structlog.stdlib import LoggerFactory
from structlog.threadlocal import wrap_dict

from sdc.rabbit import MessageConsumer
from sdc.rabbit import QueuePublisher

from app.processors.message_processor import MessageProcessor
from app import settings, __version__


def run():
    logging.basicConfig(format=settings.LOGGING_FORMAT,
                        datefmt="%Y-%m-%dT%H:%M:%S",
                        level=settings.LOGGING_LEVEL)

    logging.getLogger('sdc.rabbit').setLevel(logging.INFO)

    # These structlog settings allow bound fields to persist between classes
    structlog.configure(logger_factory=LoggerFactory(), context_class=wrap_dict(dict))
    logger = structlog.getLogger()

    logger.info('Starting SDX Downstream', version=__version__)

    message_processor = MessageProcessor()

    quarantine_publisher = QueuePublisher(
        urls=settings.RABBIT_URLS,
        queue=settings.RABBIT_QUARANTINE_QUEUE
    )

    message_consumer = MessageConsumer(
        durable_queue=True,
        exchange=settings.RABBIT_EXCHANGE,
        exchange_type='topic',
        rabbit_queue=settings.RABBIT_QUEUE,
        rabbit_urls=settings.RABBIT_URLS,
        quarantine_publisher=quarantine_publisher,
        process=message_processor.process
    )

    try:
        message_consumer.run()
    except KeyboardInterrupt:
        message_consumer.stop()

if __name__ == "__main__":
    run()
