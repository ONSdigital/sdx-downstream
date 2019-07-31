from app import settings
from app.helpers.request_helper import remote_call, response_ok, get_sequence_no
from sdc.rabbit.exceptions import QuarantinableError, RetryableError
from structlog import get_logger


class TransformProcessor:
    """Transforms and passes results to ftp"""

    def __init__(self, survey, ftp_conn):
        """
           survey: survey document
           ftp_conn: ftp connection , passed in for testing purposes
        """
        self._base_url = settings.SDX_TRANSFORM_CS_URL
        self.cora_surveys = settings.CORA_SURVEYS
        self.cord_surveys = settings.CORD_SURVEYS

        self.survey = survey
        self.tx_id = ""

        self.logger = get_logger()
        self._setup_logger()

        self.ftp = ftp_conn
        self._endpoint_name = self._get_transformer_endpoint_name(survey)

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
            self.logger.info(f"{self.__class__.__name__}:Successfully transformed")
            return response.content

        raise QuarantinableError("Response missing content")

    def _get_url(self):
        """Gets the transformer url"""
        sequence_no = TransformProcessor._get_sequence_number()
        return f"{self._base_url}/{self._endpoint_name}/{sequence_no}"

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

    def _get_transformer_endpoint_name(self, survey):
        """Returns the end point name based on the survey_id in the survey document"""

        if survey['survey_id'] in self.cora_surveys:
            return 'cora'
        if survey['survey_id'] in self.cord_surveys:
            return 'cord'

        return 'common-software'
