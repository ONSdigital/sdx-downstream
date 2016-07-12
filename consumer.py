from async_consumer import AsyncConsumer
import logging
from structlog import wrap_logger
import settings
from response_processor import ResponseProcessor

logging.basicConfig(filename=settings.LOGGING_LOCATION, level=settings.LOGGING_LEVEL, format=settings.LOGGING_FORMAT)

logger = logging.getLogger(__name__)

logger = wrap_logger(logger)
logger.debug("START")


class Consumer(AsyncConsumer):
    def on_message(self, unused_channel, basic_deliver, properties, body):

        logger.info('Received message # %s from %s: %s' % (basic_deliver.delivery_tag, properties.app_id, body))

        manager = ResponseProcessor(logger)
        proccessed_ok = manager.process(body.decode("utf-8"))

        if proccessed_ok:
            self.acknowledge_message(basic_deliver.delivery_tag)


def main():
    logger.debug("Starting consumer")
    consumer = Consumer(settings.RABBIT_URL)
    try:
        consumer.run()
    except KeyboardInterrupt:
        consumer.stop()

if __name__ == '__main__':
    main()
