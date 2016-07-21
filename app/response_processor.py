from app import settings
from app.settings import session
import zipfile
import io
import pika
from ftplib import FTP
from requests.packages.urllib3.exceptions import MaxRetryError


def connect_to_ftp():
    ftp = FTP(settings.FTP_HOST)
    ftp.login(user=settings.FTP_USER, passwd=settings.FTP_PASS)
    return ftp


def deliver_ascii_to_ftp(ftp, filename, data):
    stream = io.StringIO(data)
    ftp.storlines('STOR ' + filename, stream)


def deliver_binary_to_ftp(ftp, filename, data):
    stream = io.BytesIO(data)
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

            if 'file-type' in survey_response and survey_response['file-type'] == 'xml':
                xml_content = self.transform_xml(survey_response)

                if xml_content:
                    processed_ok = self.notify_queue(xml_content)

                return processed_ok
            else:
                zip_contents = self.transform_cs(sequence_no, survey_response)

                if zip_contents:
                    processed_ok = self.process_zip(zip_contents)

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

    def process_zip(self, zip_contents):
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
                self.logger.debug("Processing file from zip", filename=filename)
                edc_file = z.open(filename)
                deliver_binary_to_ftp(ftp, filename, edc_file.read())
            ftp.quit()
            return True

        except (RuntimeError, zipfile.BadZipfile) as e:
            self.logger.error("Bad zip file", exception=e)
            return False

    def notify_queue(self, survey_xml):
        """Method to process the content of a census 2016 response

        :rtype boolean: Whether the queue was notified successfully

        """
        try:
            self.logger.debug("XML Queueing Start")
            connection = pika.BlockingConnection(pika.URLParameters(settings.RABBIT_URL))
            channel = connection.channel()
            channel.queue_declare(queue=settings.RABBIT_QUEUE_TESTFORM)
            channel.basic_publish(exchange='',
                                  properties=pika.BasicProperties(content_type='application/xml'),
                                  routing_key=settings.RABBIT_QUEUE_TESTFORM,
                                  body=survey_xml)
            self.logger.debug("XML Queuing Success")
            connection.close()
            return True
        except:
            self.logger.error("XML Queuing Failed")
            return False
