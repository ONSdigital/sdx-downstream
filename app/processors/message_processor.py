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

    def process(self, msg, tx_id):

        if tx_id is None:
            tx_id = msg

        self.logger.info(
            'Received message',
            tx_id=tx_id,
        )

        document = get_doc_from_store(tx_id)
        if document['survey_id'] == '144':
            cora_processor = CoraProcessor(self.logger, document, self._ftp)

            cora_processor.process()
            cora_processor.logger.info("Processed successfully",
                                       tx_id=cora_processor.tx_id,
                                       )
        else:
            cs_processor = CommonSoftwareProcessor(self.logger, document, self._ftp)

            cs_processor.process()
            cs_processor.logger.info("Processed successfully",
                                     tx_id=cs_processor.tx_id,
                                     )
