from app import settings

from sdc.rabbit.exceptions import QuarantinableError, RetryableError

from app.helpers.request_helper import remote_call, get_sequence_no, response_ok


class CommonSoftwareProcessor(object):

    def __init__(self, logger, survey, ftpconn):
        self.logger = logger
        self.survey = survey
        self.tx_id = ""
        self._setup_logger()
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

        if response_ok(response) and response.content is not None:
            self.logger.info("Successfully transformed")
            return response.content
        else:
            raise QuarantinableError("Response missing content")

    def _get_ftp_folder(self, survey):
        if 'heartbeat' in survey and survey['heartbeat'] is True:
            return settings.FTP_HEARTBEAT_FOLDER
        else:
            return settings.FTP_FOLDER
