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
        # Trigger behaviour
        self.process_document(body.decode("utf-8"))
        self.acknowledge_message(basic_deliver.delivery_tag)

    def response_ok(self, res, error_on_fail, **kwargs):
        if res.status_code != 200:
            self.logger.error(error_on_fail, request_url=res.url, **kwargs)
            return False
        return True

    def process_document(self, mongoid):
        store_url = settings.SDX_STORE_URL + "/responses/" + mongoid

        r = remote_call(store_url)

        if not self.response_ok(r, "Store retrieval failed", document_id=mongoid):
            return

        result = r.json()
        stored_json = result['survey_response']
        metadata = stored_json['metadata']

        # Update consumers logger to use bound vars
        self.logger = logger.bind(user_id=metadata['user_id'], ru_ref=metadata['ru_ref'])

        sequence_url = settings.SDX_SEQUENCE_URL + "/sequence"

        r = remote_call(sequence_url)

        if not self.response_ok(r, "Sequence retrieval failed"):
            return

        result = r.json()
        sequence_no = result['sequence_no']

        transform_url = "%s/common-software/%d" % (settings.SDX_TRANSFORM_CS_URL, sequence_no)
        r = remote_call(transform_url, json=stored_json)

        if not self.response_ok(r, "Transform failed", sequence_no=sequence_no):
            return

        self.process_zip(r.content)

    def process_zip(self, zip_contents):
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

        except (RuntimeError, zipfile.BadZipfile) as e:
            self.logger.error("Bad zip file", exception=e)
            # TODO: Need to deal with exception


def main():
    logger.debug("Starting consumer")
    consumer = Consumer(settings.RABBIT_URL)
    try:
        consumer.run()
    except KeyboardInterrupt:
        consumer.stop()

if __name__ == '__main__':
    main()
