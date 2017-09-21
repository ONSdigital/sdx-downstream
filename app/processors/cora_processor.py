from sdc.rabbit.exceptions import QuarantinableError, RetryableError

from app import settings
from app.helpers.request_helper import get_sequence_no, remote_call, response_ok


class CoraProcessor(object):

    def __init__(self, logger, survey, ftpconn):
        self.logger = logger
        self.survey = survey
        self.tx_id = None
        self._setup_logger()
        self.ftp = ftpconn

    def process(self):
        transformed = self._transform()

        delivered = self.ftp.unzip_and_deliver(self._get_ftp_folder(self.survey), transformed)

        if not delivered:
            self.logger.error("Failed to deliver zip to ftp")
            raise RetryableError("Failed to deliver zip to ftp")

        return

    def _setup_logger(self):
        if self.survey:
            try:
                metadata = self.survey['metadata']
                self.logger = self.logger.bind(user_id=metadata['user_id'], ru_ref=metadata['ru_ref'])
            except KeyError:
                self.logger.error("Failed to get metadata")

            if 'tx_id' in self.survey:
                self.tx_id = self.survey['tx_id']
                self.logger = self.logger.bind(tx_id=self.tx_id)

    @staticmethod
    def _get_url():
        sequence_no = get_sequence_no()
        if sequence_no is None:
            raise RetryableError("Failed to get sequence number")

        return "{0}/cora/{1}".format(settings.SDX_TRANSFORM_CORA_URL, sequence_no)

    def _transform(self):
        endpoint = self._get_url()
        self.logger.info("Calling transform", request_url=endpoint)

        response = remote_call(endpoint, json=self.survey)

        if response_ok(response) and response.content is not None:
            self.logger.info("Successfully transformed")
            return response.content
        else:
            raise QuarantinableError("Response missing content")

    @staticmethod
    def _get_ftp_folder(survey):
        if 'heartbeat' in survey and survey['heartbeat'] is True:
            return settings.FTP_HEARTBEAT_FOLDER
        else:
            return settings.FTP_FOLDER
