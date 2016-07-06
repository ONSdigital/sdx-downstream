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

def transform_xml(stored_json):
    transform_url = "%s/xml" % (settings.SDX_TRANSFORM_TESTFORM_URL)
    transformed_data = requests.post(transform_url, json=stored_json)
    queue_notification(transformed_data.content)

def queue_notification(notification):
    connection = pika.BlockingConnection(pika.URLParameters(settings.RABBIT_URL))
    channel = connection.channel()
    channel.queue_declare(queue=settings.RABBIT_QUEUE_XML)
    channel.basic_publish(exchange='',
                          properties=pika.BasicProperties(content_type='application/xml'),
                          routing_key=settings.RABBIT_QUEUE_XML,
                          body=notification)
    logging.debug(notification)
    connection.close()

def transform_cs(stored_json, sequence_no):
    transform_url = "%s/common-software/%d" % (settings.SDX_TRANSFORM_CS_URL, sequence_no)
    transformed_data = requests.post(transform_url, json=stored_json)
    zip_contents = transformed_data.content

    try:
        z = zipfile.ZipFile(io.BytesIO(zip_contents))
        logging.debug("Zip contents:")
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

    if 'file-type' in stored_json and stored_json['file-type'] == 'xml':
        transform_xml(stored_json)
    else:
        transform_cs(stored_json, sequence_no)

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
