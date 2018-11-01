from structlog import get_logger
import requests
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.exceptions import MaxRetryError
from requests.exceptions import ConnectionError
from sdc.rabbit.exceptions import RetryableError, QuarantinableError

from app.settings import SDX_SEQUENCE_URL, SDX_STORE_URL

logger = get_logger()

# Configure the number of retries attempted before failing call
session = requests.Session()

retries = Retry(total=5, backoff_factor=0.1)

session.mount('http://', HTTPAdapter(max_retries=retries))
session.mount('https://', HTTPAdapter(max_retries=retries))


def service_name(url=None):
    """
    Attempt to get service being accessed by looking for keywords inside the url
    :returns: Service name, or None if url doesn't contain a recognised keyword
    """
    try:
        parts = url.split('/')
        if 'responses' in parts:
            return 'SDX_STORE'
        elif 'sequence' in parts:
            return 'SDX_SEQUENCE'
        elif 'common-software' in parts:
            return 'SDX_TRANSFORM_CS'
        elif 'cora' in parts:
            return 'SDX_TRANSFORM_CORA'
        else:
            return None
    except AttributeError:
        logger.exception("Service name not found")


def remote_call(url, json=None):
    service = service_name(url)

    try:
        logger.info("Calling service", request_url=url, service=service)
        response = None

        if json:
            response = session.post(url, json=json)
        else:
            response = session.get(url)

        return response

    except MaxRetryError:
        logger.error("Max retries exceeded", request_url=url)
        raise RetryableError("Max retries exceeded")
    except ConnectionError:
        logger.error("Connection error", request_url=url)
        raise RetryableError("Connection error")


def response_ok(response):
    service = service_name(response.url)

    if response.status_code == 200:
        logger.info("Returned from service", request_url=response.url, status=response.status_code, service=service)
        return True
    elif response.status_code == 404:
        logger.info("Not Found response returned from service",
                    request_url=response.url,
                    status=response.status_code,
                    service=service,
                    )
        raise QuarantinableError("Not Found response returned from {}".format(service))
    elif 400 <= response.status_code < 500:
        logger.info("Bad Request response from service",
                    request_url=response.url,
                    status=response.status_code,
                    service=service,
                    )
        raise QuarantinableError("Bad Request response from {}".format(service))

    logger.info("Bad response from service",
                request_url=response.url,
                status=response.status_code,
                service=service,
                )
    raise RetryableError("Bad response from {}".format(service))


def get_sequence_no():
    sequence_url = "{0}/sequence".format(SDX_SEQUENCE_URL)
    response = remote_call(sequence_url)

    if response_ok(response):
        return response.json().get('sequence_no')


def get_doc_from_store(tx_id):
    logger.info("About to get document from store")
    store_url = "{0}/responses/{1}".format(SDX_STORE_URL, tx_id)
    response = remote_call(store_url)

    if response_ok(response):
        logger.info("Successfully got document from store")
        return response.json()
