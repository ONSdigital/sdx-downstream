import pika
import io
import logging
from structlog import wrap_logger
import settings
import requests
import zipfile
from ftplib import FTP

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


def process_document(mongoid):
    store_url = settings.SDX_STORE_URL + "/responses/" + mongoid

    r = requests.get(store_url)

    if r.status_code != 200:
        #  Retrieval failed
        logger.error("Store retrieval failed", document_id=mongoid, request_url=store_url)

        return

    result = r.json()

    stored_json = result['survey_response']
    metadata = stored_json['metadata']

    bound_logger = logger.bind(user_id=metadata['user_id'], ru_ref=metadata['ru_ref'])

    sequence_url = settings.SDX_SEQUENCE_URL + "/sequence"
    r = requests.get(sequence_url)

    if r.status_code != 200:
        bound_logger.error("Sequence retrieval failed", request_url=sequence_url)
        return

    result = r.json()
    sequence_no = result['sequence_no']

    transform_url = "%s/common-software/%d" % (settings.SDX_TRANSFORM_CS_URL, sequence_no)
    r = requests.post(transform_url, json=stored_json)

    if r.status_code != 200:
        bound_logger.error("Transform failed", request_url=transform_url, sequence_no=sequence_no)
        return

    zip_contents = r.content

    try:
        z = zipfile.ZipFile(io.BytesIO(zip_contents))
        bound_logger.debug("Unzipped contents", filelist=z.namelist())
        ftp = connect_to_ftp()
        for filename in z.namelist():
            if filename.endswith('/'):
                continue
            bound_logger.debug("Processing file from zip", filename=filename)
            edc_file = z.open(filename)
            deliver_binary_to_ftp(ftp, filename, edc_file.read())
        ftp.quit()

    except (RuntimeError, zipfile.BadZipfile) as e:
        bound_logger.error("Bad zip file", exception=e)
        # TODO: Need to deal with exception


def on_message(channel, method_frame, header_frame, body):
    logger.debug(method_frame.delivery_tag)
    process_document(body.decode("utf-8"))
    channel.basic_ack(delivery_tag=method_frame.delivery_tag)

connection = pika.BlockingConnection(pika.URLParameters(settings.RABBIT_URL))
channel = connection.channel()
channel.queue_declare(queue=settings.RABBIT_QUEUE)
channel.basic_consume(on_message, settings.RABBIT_QUEUE)

try:
    channel.start_consuming()
except KeyboardInterrupt:
    channel.stop_consuming()

connection.close()
