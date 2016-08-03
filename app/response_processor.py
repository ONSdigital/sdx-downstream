from app.settings import logger
from app.transforms.transform_factory import TransformFactory
from app.helpers.request_helper import get_doc_from_store


class ResponseProcessor:

    def __init__(self):
        self.tx_id = None

    def process(self, mongoid):
        processed_ok = False
        survey = get_doc_from_store(mongoid)

        if survey:
            self.setup_logger(survey)
            transform = TransformFactory.get_transform(survey)
            processed_ok = transform.process()

        return processed_ok

    def setup_logger(self, survey):
        if survey:
            if 'metadata' in survey:
                metadata = survey['metadata']
                logger.bind(user_id=metadata['user_id'], ru_ref=metadata['ru_ref'])

            if 'tx_id' in survey:
                self.tx_id = survey['tx_id']
                logger.bind(tx_id=self.tx_id)
