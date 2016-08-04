from app.settings import logger
from app.async_consumer import AsyncConsumer
from app.helpers.request_helper import get_doc_from_store
from app.processors.common_software_processor import CommonSoftwareProcessor
from app.processors.census_processor import CensusProcessor

SURVEY_ID_TO_PROCESSOR = {'023': CommonSoftwareProcessor,
                          '0': CensusProcessor}


class Consumer(AsyncConsumer):

    def on_message(self, unused_channel, basic_deliver, properties, body):
        logger.info('Received message', delivery_tag=basic_deliver.delivery_tag, app_id=properties.app_id, body=body)
        try:
            mongo_id = body.decode("utf-8")
            document = get_doc_from_store(mongo_id)

            processor = self.get_processor(document)
            if processor.process():
                self.acknowledge_message(basic_deliver.delivery_tag, tx_id=processor.tx_id)

        except Exception as e:
            logger.error("ResponseProcessor failed", exception=e, tx_id=processor.tx_id)

    def get_processor(self, survey):
        try:
            survey_id = survey['survey_id']
            processor = SURVEY_ID_TO_PROCESSOR[survey_id]
            return processor(logger, survey)

        except KeyError as e:
            logger.error("Unable to get transform for survey id", exception=e)
            return None


def main():
    logger.debug("Starting consumer")
    consumer = Consumer()
    try:
        consumer.run()
    except KeyboardInterrupt:
        consumer.stop()

if __name__ == '__main__':
    main()
