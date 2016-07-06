import logging
import os
import requests
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

LOGGING_FORMAT = "%(asctime)s|%(levelname)s: sdx-downstream: %(message)s"
LOGGING_LOCATION = "logs/downstream.log"
LOGGING_LEVEL = logging.DEBUG

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
APP_TMP = os.path.join(APP_ROOT, 'tmp')

# Default to true, cast to boolean
SDX_STORE_URL = os.getenv("SDX_STORE_URL", "http://sdx-store:5000")
SDX_TRANSFORM_CS_URL = os.getenv("SDX_TRANSFORM_CS_URL", "http://sdx-transform-cs:5000")
SDX_SEQUENCE_URL = os.getenv("SDX_SEQUENCE_URL", "http://sdx-sequence:5000")

FTP_HOST = os.getenv('FTP_HOST', 'pure-ftpd')
FTP_USER = os.getenv('FTP_USER')
FTP_PASS = os.getenv('FTP_PASS')

RABBIT_QUEUE = os.getenv('RABBITMQ_QUEUE', 'sdx-survey-notifications')

RABBIT_URL = 'amqp://{user}:{password}@{hostname}:{port}/{vhost}?connection_attempts={connection_attempts}&retry_delay={retry_delay}'.format(
    hostname=os.getenv('RABBITMQ_HOST', 'rabbit'),
    port=os.getenv('RABBITMQ_PORT', 5672),
    user=os.getenv('RABBITMQ_DEFAULT_USER', 'rabbit'),
    password=os.getenv('RABBITMQ_DEFAULT_PASS', 'rabbit'),
    vhost=os.getenv('RABBITMQ_DEFAULT_VHOST', '%2f'),
    connection_attempts=os.getenv('RABBITMQ_DEFAULT_CONN_ATTEMPTS', 5),
    retry_delay=os.getenv('RABBITMQ_DEFAULT_RETRY_DELAY', 5)
)

# Configure the number of retries attempted before failing call
session = requests.Session()

retries = Retry(total=5, backoff_factor=0.1)

session.mount('http://', HTTPAdapter(max_retries=retries))
session.mount('https://', HTTPAdapter(max_retries=retries))
