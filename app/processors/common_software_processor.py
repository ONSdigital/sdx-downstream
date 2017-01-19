from app import settings
from app.helpers.request_helper import remote_call, response_ok, get_sequence_no
import SDXFTP


class CommonSoftwareProcessor(object):

    def __init__(self, logger, survey):
        self.logger = logger
        self.survey = survey
        self.tx_id = None
        self.setup_logger()
        self.ftp = SDXFTP(settings.FTP_HOST, settings.FTP_USER, settings.FTP_PASS)
        return

    def setup_logger(self):
        if self.survey:
            if 'metadata' in self.survey:
                metadata = self.survey['metadata']
                self.logger = self.logger.bind(user_id=metadata['user_id'], ru_ref=metadata['ru_ref'])

            if 'tx_id' in self.survey:
                self.tx_id = self.survey['tx_id']
                self.logger = self.logger.bind(tx_id=self.tx_id)

    def get_url(self):
        sequence_no = get_sequence_no()
        return "{0}/common-software/{1}".format(settings.SDX_TRANSFORM_CS_URL, sequence_no)

    def transform(self):
        response = remote_call(self.get_url(), json=self.survey)
        if not response or not response_ok(response):
            return None

        return response.content

    def deliver_zip(self, zip_contents):
        folder = self.get_ftp_folder(self.survey)
        return self.ftp.unzip_and_deliver(folder, zip_contents)

    def process(self):
        zip_contents = self.transform()
        if zip_contents is None:
            return False

        return self.deliver_zip(zip_contents)

    def get_ftp_folder(self, survey):
        if 'heartbeat' in survey and survey['heartbeat'] is True:
            return settings.FTP_HEARTBEAT_FOLDER
        else:
            return settings.FTP_FOLDER
