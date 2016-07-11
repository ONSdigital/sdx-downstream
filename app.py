from async_consumer import AsyncConsumer
import io
import logging
from structlog import wrap_logger
import settings
from settings import session
import zipfile
from ftplib import FTP
from requests.packages.urllib3.exceptions import MaxRetryError

logging.basicConfig(filename=settings.LOGGING_LOCATION, level=settings.LOGGING_LEVEL, format=settings.LOGGING_FORMAT)

logger = wrap_logger(
    logging.getLogger(__name__)
)
logger.debug("START")


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


def remote_call(request_url, json=None):
    try:
        r = None

        if json:
            r = session.post(request_url, json=json)
        else:
            r = session.get(request_url)

        return r
    except MaxRetryError:
        logger.error("Max retries exceeded (5)", request_url=request_url)


class Consumer(AsyncConsumer):
    def on_message(self, unused_channel, basic_deliver, properties, body):

        logger.info('Received message # %s from %s: %s' % (basic_deliver.delivery_tag, properties.app_id, body))

        survey_response = self.get_doc_from_store(body.decode("utf-8"))

        if survey_response:
            sequence_no = self.get_sequence_no()

        if survey_response and sequence_no:
            zip_contents = self.transform_response(sequence_no, survey_response)

            if zip_contents:
                zip_ok = self.process_zip(zip_contents)

        if zip_ok:
            self.acknowledge_message(basic_deliver.delivery_tag)

    def response_ok(self, res, error_on_fail, **kwargs):
        if res.status_code != 200:
            logger.error(error_on_fail, request_url=res.url, **kwargs)
            return False
        return True

    def get_doc_from_store(self, mongoid):
        """Retrieve a doc from the store. Bind a logger to a user/ru_ref

        :rtype boolean: Whether the doc was retrieved successfully

        """
        store_url = settings.SDX_STORE_URL + "/responses/" + mongoid

        r = remote_call(store_url)

        if not self.response_ok(r, "Store retrieval failed", document_id=mongoid):
            return False

        result = r.json()
        stored_json = result['survey_response']
        metadata = stored_json['metadata']

        # Update consumers logger to use bound vars
        self.logger = logger.bind(user_id=metadata['user_id'], ru_ref=metadata['ru_ref'])

        return stored_json

    def get_sequence_no(self):
        sequence_url = settings.SDX_SEQUENCE_URL + "/sequence"

        r = remote_call(sequence_url)

        if not self.response_ok(r, "Sequence retrieval failed"):
            return False

        result = r.json()
        return result['sequence_no']

    def transform_response(self, sequence_no, survey_response):
        transform_url = "%s/common-software/%d" % (settings.SDX_TRANSFORM_CS_URL, sequence_no)
        r = remote_call(transform_url, json=survey_response)

        if not self.response_ok(r, "Transform failed", sequence_no=sequence_no):
            return False

        return r.content

    def process_zip(self, zip_contents):
        """Method to process the content of a response

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


def main():
    logger.debug("Starting consumer")
    consumer = Consumer(settings.RABBIT_URL)
    try:
        consumer.run()
    except KeyboardInterrupt:
        consumer.stop()

if __name__ == '__main__':
    main()
