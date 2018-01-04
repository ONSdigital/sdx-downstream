import json
import logging
import os
from structlog import wrap_logger


LOGGING_LEVEL = logging.getLevelName(os.getenv("LOGGING_LEVEL", "DEBUG"))
LOGGING_FORMAT = "%(asctime)s.%(msecs)06dZ|%(levelname)s: sdx-downstream: %(message)s"

logger = wrap_logger(
    logging.getLogger(__name__)
)

HEARTBEAT_INTERVAL = "?heartbeat_interval=5"


def _get_value(key, default_value=None):
    """Gets a value from an environment variable , will use default if present else raise a value Error
    """
    value = os.getenv(key, default_value)
    if not value:
        logger.error("No value set for {}".format(key))
        raise ValueError()
    return value


def parse_vcap_services():
    vcap_services = _get_value("VCAP_SERVICES")
    parsed_vcap_services = json.loads(vcap_services)
    rabbit_config = parsed_vcap_services.get('rabbitmq')
    rabbit_url = rabbit_config[0].get('credentials').get('uri') + HEARTBEAT_INTERVAL
    rabbit_url2 = rabbit_config[1].get('credentials').get('uri') + HEARTBEAT_INTERVAL if len(rabbit_config) > 1 else rabbit_url
    return rabbit_url, rabbit_url2


def parse_non_vcap_services():
    rabbit_url = 'amqp://{user}:{password}@{hostname}:{port}/{vhost}'.format(
        hostname=_get_value('RABBITMQ_HOST', 'rabbit'),
        port=_get_value('RABBITMQ_PORT', 5672),
        user=_get_value('RABBITMQ_DEFAULT_USER', 'rabbit'),
        password=_get_value('RABBITMQ_DEFAULT_PASS', 'rabbit'),
        vhost=_get_value('RABBITMQ_DEFAULT_VHOST', '%2f')
    ) + HEARTBEAT_INTERVAL

    rabbit_url2 = 'amqp://{user}:{password}@{hostname}:{port}/{vhost}'.format(
        hostname=_get_value('RABBITMQ_HOST2', 'rabbit'),
        port=_get_value('RABBITMQ_PORT2', 5672),
        user=_get_value('RABBITMQ_DEFAULT_USER', 'rabbit'),
        password=_get_value('RABBITMQ_DEFAULT_PASS', 'rabbit'),
        vhost=_get_value('RABBITMQ_DEFAULT_VHOST', '%2f')
    ) + HEARTBEAT_INTERVAL
    return rabbit_url, rabbit_url2


if os.getenv("CF_DEPLOYMENT", False):
    RABBIT_URL, RABBIT_URL2 = parse_vcap_services()
else:
    RABBIT_URL, RABBIT_URL2 = parse_non_vcap_services()

RABBIT_URLS = [RABBIT_URL, RABBIT_URL2]
RABBIT_QUEUE = 'sdx-survey-notification-durable'
RABBIT_EXCHANGE = 'message'
RABBIT_QUARANTINE_QUEUE = os.getenv('RABBIT_QUARANTINE_QUEUE', 'sdx-downstream-quarantine')

FTP_HOST = _get_value('FTP_HOST', 'pure-ftpd')
FTP_USER = os.getenv('FTP_USER')
FTP_PASS = os.getenv('FTP_PASS')
FTP_FOLDER = '/'

SDX_STORE_URL = _get_value("SDX_STORE_URL", "http://sdx-store:5000")
SDX_TRANSFORM_CS_URL = _get_value("SDX_TRANSFORM_CS_URL", "http://sdx-transform-cs:5000")
SDX_TRANSFORM_CORA_URL = _get_value("SDX_TRANSFORM_CORA_URL", "http://sdx-transform-cora:5000")
SDX_SEQUENCE_URL = _get_value("SDX_SEQUENCE_URL", "http://sdx-sequence:5000")

CORA_SURVEYS = ['144']
