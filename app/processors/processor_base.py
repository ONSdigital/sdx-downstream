from app import settings
from app.helpers.request_helper import remote_call, response_ok, get_sequence_no
from sdc.rabbit.exceptions import QuarantinableError, RetryableError


class Processor:
    """Abstract base class with common functionality between Cora and common software classes
        Child classes should implement _setup_logger() and _get_url(), this class does NOT verify that they do
    """
    def __init__(self, logger, survey, ftpconn):
        self.logger = logger
        self.survey = survey
        self.tx_id = ""
        self._setup_logger()
        self.ftp = ftpconn
        return

    def process(self):
        """call transform and error if needed"""
        transformed = self._transform()

        delivered = self.ftp.unzip_and_deliver(self._get_ftp_folder(self.survey), transformed)

        if not delivered:
            self.logger.error("Failed to deliver zip to ftp")
            raise RetryableError("Failed to deliver zip to ftp")

        return

    def _transform(self):
        """ call the transform endpoint and raise quarantinable error if bad response"""
        endpoint = self._get_url()
        self.logger.info("Calling transform", request_url=endpoint)

        response = remote_call(endpoint, json=self.survey)

        if response_ok(response) and response.content is not None:
            self.logger.info("{}:Successfully transformed".format(self.__class__.__name__))
            return response.content
        else:
            raise QuarantinableError("Response missing content")

    @staticmethod
    def _get_sequence_number():
        """return the sequence number else raise a Retryable Error"""
        sequence_no = get_sequence_no()
        if sequence_no is None:
            raise RetryableError("Failed to get sequence number")
        return sequence_no

    @staticmethod
    def _get_ftp_folder(survey):
        """return the destination folder as a string """
        if 'heartbeat' in survey and survey['heartbeat'] is True:
            return settings.FTP_HEARTBEAT_FOLDER
        else:
            return settings.FTP_FOLDER
