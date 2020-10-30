import json

from structlog import get_logger


from app.helpers.request_helper import get_doc_from_store, get_feedback_from_store
from app.processors.transform_processor import TransformProcessor
from app.helpers.sdxftp import SDXFTP
from app import settings


class MessageProcessor:
    def __init__(self):
        self.logger = get_logger()
        self.ftp = SDXFTP(settings.FTP_HOST, settings.FTP_USER, settings.FTP_PASS)

    def process(self, msg, tx_id):
        id_tag = json.loads(msg)
        if tx_id is None:
            tx_id = id_tag.get('tx_id')

        self.logger = self.logger.bind(tx_id=tx_id)
        self.logger.info('Received message')

        try:

            if id_tag.get('is_feedback'):
                feedback_id = id_tag.get('feedback_id')
                document = get_feedback_from_store(feedback_id)
                data = json.dumps(document).encode('utf-8')
                filename = 'feedback_{}'.format(feedback_id)
                self.ftp.deliver_binary(settings.FTP_FEEDBACK_FOLDER, filename, data)
            else:
                document = get_doc_from_store(tx_id)
                transform_processor = TransformProcessor(document, self.ftp)
                transform_processor.process()

            self.logger.info("Processed successfully")

            # If we don't unbind these fields, their current value will be retained for the next
            # submission.  This leads to incorrect values being logged out in the bound fields.
            self.logger = self.logger.unbind("tx_id", "ru_ref", "user_id")
        except KeyError:
            self.logger.error("No survey ID in document")
