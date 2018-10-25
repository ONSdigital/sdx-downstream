from structlog import get_logger

from app.helpers.request_helper import get_doc_from_store
from app.processors.common_software_processor import CommonSoftwareProcessor
from app.processors.cora_processor import CoraProcessor
from app import settings
from app.helpers.sdxftp import SDXFTP


class MessageProcessor:
    def __init__(self):
        self.logger = get_logger()
        self._ftp = SDXFTP(settings.FTP_HOST, settings.FTP_USER, settings.FTP_PASS)
        self.cora_surveys = settings.CORA_SURVEYS

    def process(self, msg, tx_id):

        if tx_id is None:
            tx_id = msg

        self.logger = self.logger.bind(tx_id=tx_id)
        self.logger.info('Received message')

        document = get_doc_from_store(tx_id)

        try:
            processor = self._get_processor(document)
            processor.process()
            processor.logger.info("Processed successfully")

        except KeyError:
            self.logger.error("No survey ID in document")

    def _get_processor(self, document):
        """Processor factory that returns the correct processor based on the survey_id in the document"""

        if document['survey_id'] in self.cora_surveys:
            return CoraProcessor(document, self._ftp)

        return CommonSoftwareProcessor(document, self._ftp)
