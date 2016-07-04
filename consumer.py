import pika
import io
import logging
import sys
import settings
import requests
import zipfile
from ftplib import FTP

logging.basicConfig(stream=sys.stdout, level=settings.LOGGING_LEVEL, format=settings.LOGGING_FORMAT)

logging.debug("sdx-downstream|START")


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


def get_survey_from_store(mongoid):
    store_url = settings.SDX_STORE_URL + "/responses/" + mongoid
    result = requests.get(store_url).json()
    stored_json = result['survey_response']

    sequence_url = settings.SDX_SEQUENCE_URL + "/sequence"
    result = requests.get(sequence_url).json()
    sequence_no = result['sequence_no']

    if stored_json['file-type'] == 'xml':
        transform_url = "%s/xml/%d" % (settings.SDX_TRANSFORM_XML_URL, sequence_no)
    else:
        transform_url = "%s/common-software/%d" % (settings.SDX_TRANSFORM_CS_URL, sequence_no)

    transformed_data = requests.post(transform_url, json=stored_json)
    logging.debug(transformed_data)
    zip_contents = transformed_data.content

    try:
        z = zipfile.ZipFile(io.BytesIO(zip_contents))
        logging.debug(z.namelist())
        ftp = connect_to_ftp()
        for filename in z.namelist():
            if filename.endswith('/'):
                continue
            logging.debug("Processing file from zip: " + filename)
            edc_file = z.open(filename)
            deliver_binary_to_ftp(ftp, filename, edc_file.read())
        ftp.quit()

    except (RuntimeError, zipfile.BadZipfile):
        logging.debug("Bad zip file!")
        # TODO: Need to deal with exception

def on_message(channel, method_frame, header_frame, body):
    logging.debug(method_frame.delivery_tag)
    get_survey_from_store(body.decode("utf-8"))
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
