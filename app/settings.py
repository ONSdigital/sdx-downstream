import logging
from structlog import wrap_logger
import os
import requests
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

LOGGING_FORMAT = "%(asctime)s|%(levelname)s: sdx-downstream: %(message)s"
LOGGING_LEVEL = logging.getLevelName(os.getenv('LOGGING_LEVEL', 'DEBUG'))

logging.basicConfig(level=LOGGING_LEVEL, format=LOGGING_FORMAT)
logger = wrap_logger(logging.getLogger(__name__))

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
APP_TMP = os.path.join(APP_ROOT, 'tmp')

# Default to true, cast to boolean
SDX_STORE_URL = os.getenv("SDX_STORE_URL", "http://sdx-store:5000")
SDX_TRANSFORM_CS_URL = os.getenv("SDX_TRANSFORM_CS_URL", "http://sdx-transform-cs:5000")
SDX_TRANSFORM_TESTFORM_URL = os.getenv("SDX_TRANSFORM_TESTFORM_URL", "http://sdx-transform-testform:5000")
SDX_SEQUENCE_URL = os.getenv("SDX_SEQUENCE_URL", "http://sdx-sequence:5000")

FTP_HOST = os.getenv('FTP_HOST', 'pure-ftpd')
FTP_USER = os.getenv('FTP_USER')
FTP_PASS = os.getenv('FTP_PASS')

FTP_FOLDER = os.getenv('FTP_FOLDER', '/')
FTP_HEARTBEAT_FOLDER = os.getenv('FTP_HEARTBEAT_FOLDER', '/heartbeat')

RABBIT_QUEUE = os.getenv('RABBITMQ_QUEUE', 'sdx-survey-notifications')
RABBIT_DELAY_QUEUE = os.getenv('RABBIT_DELAY_QUEUE', 'sdx-survey-notifications_delay')
RABBIT_QUEUE_TESTFORM = os.getenv('RABBIT_QUEUE_TESTFORM', 'sdx-testform')
RABBIT_EXCHANGE = os.getenv('RABBITMQ_EXCHANGE', 'message')

QUEUE_RETRY_DELAY_IN_MS = 20000
QUEUE_MAX_MESSAGE_DELIVERIES = 3

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

RABBIT_URLS = [RABBIT_URL, RABBIT_URL2]

# Configure the number of retries attempted before failing call
session = requests.Session()

retries = Retry(total=5, backoff_factor=0.1)

session.mount('http://', HTTPAdapter(max_retries=retries))
session.mount('https://', HTTPAdapter(max_retries=retries))
