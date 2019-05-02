from app import settings
from app.helpers.request_helper import remote_call, response_ok, get_sequence_no
from sdc.rabbit.exceptions import QuarantinableError, RetryableError
from structlog import get_logger


class Processor:
    """Base class calls transformer and passes results to ftp"""

    def __init__(self, survey, ftpconn, base_url, endpoint_name):
        self.logger = get_logger()
        self.survey = survey
        self.tx_id = ""
        self._setup_logger()
        self.ftp = ftpconn
        self._base_url = base_url
        self._endpoint_name = endpoint_name

    def process(self):
        """call transform and error if needed"""
        transformed = self._transform()
        delivered = self.ftp.unzip_and_deliver(settings.FTP_FOLDER, transformed)

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

        raise QuarantinableError("Response missing content")

    def _get_url(self):
        """Gets the transformer url"""
        sequence_no = Processor._get_sequence_number()
        return "{0}/{1}/{2}".format(self._base_url, self._endpoint_name, sequence_no)

    def _setup_logger(self):
        """Sets up the logger"""
        if self.survey:
            try:
                metadata = self.survey['metadata']
                self.logger = self.logger.bind(user_id=metadata['user_id'], ru_ref=metadata['ru_ref'])
            except KeyError:
                self.logger.error("Failed to get metadata")

    @staticmethod
    def _get_sequence_number():
        """return the sequence number else raise a Retryable Error"""
        sequence_no = get_sequence_no()
        if sequence_no is None:
            raise RetryableError("Failed to get sequence number")
        return sequence_no
