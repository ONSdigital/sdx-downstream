from app import settings
from app.helpers.request_helper import remote_call, response_ok, get_sequence_no
from app.helpers.ftp_helper import get_ftp_folder, process_zip_to_ftp
from app.processors.survey_processor import SurveyProcessor


class CommonSoftwareProcessor(SurveyProcessor):

    def get_url(self):
        sequence_no = get_sequence_no()
        return "{0}/common-software/{1}".format(settings.SDX_TRANSFORM_CS_URL, sequence_no)

    def transform(self):
        response = remote_call(self.get_url(), json=self.survey)
        if not response or not response_ok(response):
            return None

        return response.content

    def deliver_zip(self, zip_contents):
        folder = get_ftp_folder(self.survey)
        return process_zip_to_ftp(folder, zip_contents)

    def process(self):
        zip_contents = self.transform()
        if zip_contents is None:
            return False

        return self.deliver_zip(zip_contents)
