import logging

from structlog import wrap_logger

from app.helpers.request_helper import get_doc_from_store
from app.processors.common_software_processor import CommonSoftwareProcessor
from app.processors.cora_processor import CoraProcessor
from app import settings
from app.helpers.sdxftp import SDXFTP


class MessageProcessor:
    def __init__(self, logger=None):
        self.logger = logger or wrap_logger(logging.getLogger(__name__))
        self._ftp = SDXFTP(self.logger, settings.FTP_HOST, settings.FTP_USER, settings.FTP_PASS)
        self.cora_surveys = settings.CORA_SURVEYS

    def process(self, msg, tx_id):

        if tx_id is None:
            tx_id = msg

        self.logger.info(
            'Received message',
            tx_id=tx_id,
        )

        document = get_doc_from_store(tx_id)

        try:
            processor = self._get_processor(document)
            processor.process()
            processor.logger.info("Processed successfully", tx_id=processor.tx_id)

        except KeyError:
            self.logger.error("No survey ID in document")

    def _get_processor(self, document):
        """Processor factory that returns the correct processor based on the survey_id in the document"""
        processor = CoraProcessor(self.logger, document, self._ftp) \
            if document['survey_id'] in self.cora_surveys else \
            CommonSoftwareProcessor(self.logger, document, self._ftp)

        return processor
