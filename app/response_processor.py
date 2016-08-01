from app import settings
from app.settings import session
import zipfile
import io
from ftplib import FTP
from requests.packages.urllib3.exceptions import MaxRetryError
from app.queue_publisher import QueuePublisher


def connect_to_ftp():
    ftp = FTP(settings.FTP_HOST)
    ftp.login(user=settings.FTP_USER, passwd=settings.FTP_PASS)
    return ftp


def get_ftp_folder(survey):
    if 'heartbeat' in survey and survey['heartbeat'] is True:
        return settings.FTP_HEARTBEAT_FOLDER
    else:
        return settings.FTP_FOLDER


def is_census(survey):
    s_id = survey['survey_id']
    s_instrument_id = survey['collection']['instrument_id']

    survey_identifier = "{0}.{1}".format(s_id, s_instrument_id)
    if survey_identifier == settings.CENSUS_IDENTIFIER:
        return True
    else:
        return False


# TODO: is this method needed? I can't find where it is used
def deliver_ascii_to_ftp(ftp, filename, data):
    stream = io.StringIO(data)
    ftp.storlines('STOR ' + filename, stream)


def deliver_binary_to_ftp(ftp, folder, filename, data):
    stream = io.BytesIO(data)
    ftp.cwd(folder)
    ftp.storbinary('STOR ' + filename, stream)


class ResponseProcessor:
    def __init__(self, logger):
        self.logger = logger
        self.tx_id = ""

    def response_ok(self, res):
        if res.status_code == 200:
            self.logger.info("Returned from service", request_url=res.url, status_code=res.status_code)
            return True
        else:
            self.logger.error("Returned from service", request_url=res.url, status_code=res.status_code)
            return False

    def remote_call(self, request_url, json=None):
        try:
            self.logger.info("Calling service", request_url=request_url)

            r = None

            if json:
                r = session.post(request_url, json=json)
            else:
                r = session.get(request_url)

            return r
        except MaxRetryError:
            self.logger.error("Max retries exceeded (5)", request_url=request_url)

    def process(self, mongoid):
        processed_ok = False
        survey_response = self.get_doc_from_store(mongoid)

        if survey_response:
            # Update consumers logger to use bound vars
            metadata = survey_response['metadata']

            self.logger = self.logger.bind(user_id=metadata['user_id'], ru_ref=metadata['ru_ref'])

            if 'tx_id' in survey_response:
                self.tx_id = survey_response['tx_id']
                self.logger = self.logger.bind(tx_id=self.tx_id)

            sequence_no = self.get_sequence_no()

        if survey_response and sequence_no:
            if is_census(survey_response):
                xml_content = self.transform_xml(survey_response)

                if xml_content:
                    processed_ok = self.notify_queue(xml_content)

                return processed_ok
            else:
                zip_contents = self.transform_cs(sequence_no, survey_response)

                if zip_contents:
                    folder = get_ftp_folder(survey_response)
                    processed_ok = self.process_zip(folder, zip_contents)

                return processed_ok

    def get_doc_from_store(self, mongoid):
        """Retrieve a doc from the store.

        :rtype boolean: Whether the doc was retrieved successfully

        """
        store_url = settings.SDX_STORE_URL + "/responses/" + mongoid

        r = self.remote_call(store_url)

        if not self.response_ok(r):
            return False

        result = r.json()

        return result['survey_response']

    def get_sequence_no(self):
        sequence_url = settings.SDX_SEQUENCE_URL + "/sequence"

        r = self.remote_call(sequence_url)

        if not self.response_ok(r):
            return False

        result = r.json()
        return result['sequence_no']

    def transform_cs(self, sequence_no, survey_response):
        transform_url = "%s/common-software/%d" % (settings.SDX_TRANSFORM_CS_URL, sequence_no)
        r = self.remote_call(transform_url, json=survey_response)

        if not self.response_ok(r):
            return False

        return r.content

    def transform_xml(self, survey_response):
        transform_url = "%s/xml" % (settings.SDX_TRANSFORM_TESTFORM_URL)
        r = self.remote_call(transform_url, json=survey_response)

        if not self.response_ok(r):
            return False

        return r.content

    def process_zip(self, folder, zip_contents):
        """Method to process the content of a common software response

        :rtype boolean: Whether the zip was unarchived successfully

        """
        try:
            z = zipfile.ZipFile(io.BytesIO(zip_contents))
            self.logger.debug("Unzipped contents", filelist=z.namelist())
            ftp = connect_to_ftp()
            for filename in z.namelist():
                if filename.endswith('/'):
                    continue
                self.logger.debug("Processing file from zip", folder=folder, filename=filename)
                edc_file = z.open(filename)
                deliver_binary_to_ftp(ftp, folder, filename, edc_file.read())
            ftp.quit()
            return True

        except (RuntimeError, zipfile.BadZipfile) as e:
            self.logger.error("Bad zip file", exception=e)
            return False

    def notify_queue(self, survey_xml):
        """Method to process the content of a census 2016 response

        :rtype boolean: Whether the queue was notified successfully

        """
        publisher = QueuePublisher(self.logger, settings.RABBIT_URLS, settings.RABBIT_QUEUE_TESTFORM)
        return publisher.publish_message(survey_xml, 'application/xml')
