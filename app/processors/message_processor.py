from structlog import get_logger


from app.helpers.request_helper import get_doc_from_store
from app.processors.transform_processor import TransformProcessor
from app.helpers.sdxftp import SDXFTP
from app import settings


class MessageProcessor:
    def __init__(self):
        self.logger = get_logger()
        self.ftp = SDXFTP(settings.FTP_HOST, settings.FTP_USER, settings.FTP_PASS)

    def process(self, msg, tx_id):
        if tx_id is None:
            tx_id = msg

        self.logger = self.logger.bind(tx_id=tx_id)
        self.logger.info('Received message')

        document = get_doc_from_store(tx_id)

        try:
            transform_processor = TransformProcessor(document, self.ftp)
            transform_processor.process()
            self.logger.info("Processed successfully")

            # If we don't unbind these fields, their current value will be retained for the next
            # submission.  This leads to incorrect values being logged out in the bound fields.
            self.logger = self.logger.unbind("tx_id", "ru_ref", "user_id")
        except KeyError:
            self.logger.error("No survey ID in document")
