from app import settings
from app.helpers.request_helper import remote_call, response_ok, get_sequence_no
from app.helpers.ftp_helper import get_ftp_folder, process_zip_to_ftp


class CommonSoftware(object):

    def __init__(self, survey):
        self.survey = survey

    def transform(self):
        sequence_no = get_sequence_no()
        if sequence_no is False:
            return False

        url = "{0}/common-software/{1}".format(settings.SDX_TRANSFORM_CS_URL, sequence_no)
        response = remote_call(url, json=self.survey)
        if not response_ok(response):
            return False

        return response.content

    def process(self):
        zip_contents = self.transform()
        if zip_contents is False:
            return False

        folder = get_ftp_folder(self.survey)
        return process_zip_to_ftp(folder, zip_contents)
