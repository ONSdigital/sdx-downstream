import logging
from structlog import wrap_logger
from async_consumer import AsyncConsumer
import settings
from response_processor import ResponseProcessor

logging.basicConfig(level=settings.LOGGING_LEVEL, format=settings.LOGGING_FORMAT)

logger = logging.getLogger(__name__)

logger = wrap_logger(logger)


class Consumer(AsyncConsumer):
    def on_message(self, unused_channel, basic_deliver, properties, body):

        logger.info('Received message', delivery_tag=basic_deliver.delivery_tag, app_id=properties.app_id, body=body)

        processor = ResponseProcessor(logger)
        proccessed_ok = processor.process(body.decode("utf-8"))

        if proccessed_ok:
            self.acknowledge_message(basic_deliver.delivery_tag)


def main():
    logger.debug("Starting consumer")
    consumer = Consumer()
    try:
        consumer.run()
    except KeyboardInterrupt:
        consumer.stop()

if __name__ == '__main__':
    main()
