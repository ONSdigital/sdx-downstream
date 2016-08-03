from app.settings import logger, CENSUS_ID, COMMON_SOFTWARE_ID
from app.helpers.request_helper import get_doc_from_store
from app.transforms.common_software import CommonSoftware
from app.transforms.census import Census

TRANSFORM_MAP = {COMMON_SOFTWARE_ID: CommonSoftware,
                 CENSUS_ID: Census}


class ResponseProcessor:

    def __init__(self):
        self.tx_id = None

    def process(self, mongoid):
        survey = get_doc_from_store(mongoid)
        if survey is False:
            return False

        self.setup_logger(survey)

        transform = self.get_transform(survey)
        if transform is False:
            return False

        return transform.process()

    def get_transform(self, survey):
        try:
            survey_id = survey['survey_id']
            mapping = TRANSFORM_MAP[survey_id]
            return mapping(survey)

        except KeyError as e:
            logger.error("Unable to get transform for survey id", exception=e)
            return False

    def setup_logger(self, survey):
        if survey:
            if 'metadata' in survey:
                metadata = survey['metadata']
                logger.bind(user_id=metadata['user_id'], ru_ref=metadata['ru_ref'])

            if 'tx_id' in survey:
                self.tx_id = survey['tx_id']
                logger.bind(tx_id=self.tx_id)
