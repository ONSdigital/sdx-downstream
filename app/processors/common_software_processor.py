from app import settings
from app.helpers.request_helper import remote_call, get_sequence_no
from app.helpers.exceptions import BadMessageError, RetryableError


class CommonSoftwareProcessor(object):

    def __init__(self, logger, survey, ftpconn):
        self.logger = logger
        self.survey = survey
        self._setup_logger()
        self.tx_id = ""
        self.ftp = ftpconn
        return

    def process(self):
        transformed = self._transform()

        delivered = self.ftp.unzip_and_deliver(self._get_ftp_folder(self.survey), transformed)

        if not delivered:
            self.logger.error("Failed to deliver zip to ftp")
            raise RetryableError("Failed to deliver zip to ftp")

        return

    def _setup_logger(self):
        if self.survey:
            if 'metadata' in self.survey:
                metadata = self.survey['metadata']
                self.logger = self.logger.bind(user_id=metadata['user_id'], ru_ref=metadata['ru_ref'])

            if 'tx_id' in self.survey:
                self.tx_id = self.survey['tx_id']
                self.logger = self.logger.bind(tx_id=self.tx_id)

    def _get_url(self):
        sequence_no = get_sequence_no()
        if sequence_no is None:
            raise RetryableError("Failed to get sequence number")

        return "{0}/common-software/{1}".format(settings.SDX_TRANSFORM_CS_URL, sequence_no)

    def _transform(self):
        endpoint = self._get_url()
        self.logger.info("Calling transform", request_url=endpoint)

        response = remote_call(endpoint, json=self.survey)

        if response.status_code == 400 or response.content is None:
            # There was an issue with the data. This would imply the data was
            # corrupt or wrong in some way that means it cannot be trabsformed
            self.logger.error("Failed to transform", request_url=endpoint, sestatus_code=response.status_code)
            raise BadMessageError("Failure to transform")

        elif response.status_code != 200:
            # General internal error received from transformer so worth retrying.
            self.logger.error("Bad response from transformer", request_url=endpoint, status_code=response.status_code)
            raise RetryableError("Failure to transform")

        self.logger.info("Successfully transformed")
        return response.content

    def _get_ftp_folder(self, survey):
        if 'heartbeat' in survey and survey['heartbeat'] is True:
            return settings.FTP_HEARTBEAT_FOLDER
        else:
            return settings.FTP_FOLDER
