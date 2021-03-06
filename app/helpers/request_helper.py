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
        elif 'common-software' in parts or 'cord' in parts or 'cora' in parts:  # easier to read than any()
            return 'SDX_TRANSFORM_CS'
        else:
            return None
    except AttributeError:
        logger.exception("Service name not found")


def remote_call(url, json=None):
    service = service_name(url)

    try:
        logger.info("Calling service", request_url=url, service=service)

        if json:
            return session.post(url, json=json)

        return session.get(url)

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
        raise QuarantinableError(f"Not Found response returned from {service}")
    elif 400 <= response.status_code < 500:
        logger.info("Bad Request response from service",
                    request_url=response.url,
                    status=response.status_code,
                    service=service,
                    )
        raise QuarantinableError(f"Bad Request response from {service}")

    logger.info("Bad response from service",
                request_url=response.url,
                status=response.status_code,
                service=service,
                )
    raise RetryableError(f"Bad response from {service}")


def get_sequence_no():
    sequence_url = f"{SDX_SEQUENCE_URL}/sequence"
    response = remote_call(sequence_url)

    if response_ok(response):
        return response.json().get('sequence_no')


def get_doc_from_store(tx_id):
    logger.info("About to get document from store")
    store_url = f"{SDX_STORE_URL}/responses/{tx_id}"
    response = remote_call(store_url)

    if response_ok(response):
        logger.info("Successfully got document from store")
        return response.json()


def get_feedback_from_store(feedback_id):
    logger.info("About to get feedback from store", id=feedback_id)
    store_url = f"{SDX_STORE_URL}/feedback/{feedback_id}"
    response = remote_call(store_url)

    if response_ok(response):
        logger.info("Successfully got feedback from store", id=feedback_id)
        return response.json()
