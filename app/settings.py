import json
import logging
import os


LOGGING_LEVEL = logging.getLevelName(os.getenv("LOGGING_LEVEL", "DEBUG"))
LOGGING_FORMAT = "%(asctime)s.%(msecs)06dZ|%(levelname)s: sdx-downstream: %(message)s"


def parse_vcap_services():
    vcap_services = os.getenv("VCAP_SERVICES")
    parsed_vcap_services = json.loads(vcap_services)
    rabbit_config = parsed_vcap_services.get('rabbitmq')
    rabbit_url = rabbit_config[0].get('credentials').get('uri')
    rabbit_url2 = rabbit_config[1].get('credentials').get('uri') if len(rabbit_config) > 1 else rabbit_url

    ftp_config = parsed_vcap_services.get('ftp')
    ftp_user = ftp_config[0].get('ftp_user')
    ftp_pass = ftp_config[0].get('ftp_pass')

    return rabbit_url, rabbit_url2, ftp_user, ftp_pass

if os.getenv("CF_DEPLOYMENT", False):
    RABBIT_URL, RABBIT_URL2, FTP_USER, FTP_PASS = parse_vcap_services()
else:
    # Default to true, cast to boolean
    SDX_STORE_URL = os.getenv("SDX_STORE_URL", "http://sdx-store:5000")
    SDX_TRANSFORM_CS_URL = os.getenv("SDX_TRANSFORM_CS_URL", "http://sdx-transform-cs:5000")
    SDX_TRANSFORM_CORA_URL = os.getenv("SDX_TRANSFORM_CORA_URL", "http://sdx-transform-cora:5000")
    SDX_SEQUENCE_URL = os.getenv("SDX_SEQUENCE_URL", "http://sdx-sequence:5000")

    FTP_HOST = os.getenv('FTP_HOST', 'pure-ftpd')
    FTP_USER = os.getenv('FTP_USER')
    FTP_PASS = os.getenv('FTP_PASS')

    RABBIT_QUEUE = 'sdx-survey-notification-durable'
    RABBIT_EXCHANGE = 'message'
    RABBIT_QUARANTINE_QUEUE = os.getenv('RABBIT_QUARANTINE_QUEUE', 'sdx-downstream-quarantine')

    RABBIT_URL = 'amqp://{user}:{password}@{hostname}:{port}/{vhost}'.format(
        hostname=os.getenv('RABBITMQ_HOST', 'rabbit'),
        port=os.getenv('RABBITMQ_PORT', 5672),
        user=os.getenv('RABBITMQ_DEFAULT_USER', 'rabbit'),
        password=os.getenv('RABBITMQ_DEFAULT_PASS', 'rabbit'),
        vhost=os.getenv('RABBITMQ_DEFAULT_VHOST', '%2f')
    )

    RABBIT_URL2 = 'amqp://{user}:{password}@{hostname}:{port}/{vhost}'.format(
        hostname=os.getenv('RABBITMQ_HOST2', 'rabbit'),
        port=os.getenv('RABBITMQ_PORT2', 5672),
        user=os.getenv('RABBITMQ_DEFAULT_USER', 'rabbit'),
        password=os.getenv('RABBITMQ_DEFAULT_PASS', 'rabbit'),
        vhost=os.getenv('RABBITMQ_DEFAULT_VHOST', '%2f')
    )


FTP_FOLDER = '/'
FTP_HEARTBEAT_FOLDER = '/heartbeat'
CORA_SURVEYS = ['144']
RABBIT_URLS = [RABBIT_URL, RABBIT_URL2]
