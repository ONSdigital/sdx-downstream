from app.settings import logger, session, SDX_SEQUENCE_URL, SDX_STORE_URL
from requests.packages.urllib3.exceptions import MaxRetryError
from requests.exceptions import ConnectionError
from app.helpers.exceptions import RetryableError


def remote_call(url, json=None):
    try:
        logger.info("Calling service", request_url=url)
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
    if response is None:
        logger.error("No response from service")
        return False
    elif response.status_code == 200:
        logger.info("Returned from service", request_url=response.url, status_code=response.status_code)
        return True
    else:
        logger.error("Returned from service", request_url=response.url, status_code=response.status_code)
        return False


def get_sequence_no():
    sequence_url = "{0}/sequence".format(SDX_SEQUENCE_URL)
    response = remote_call(sequence_url)
    if not response_ok(response):
        logger.error("Failed to get sequence number", request_url=sequence_url)
        return None

    result = response.json()
    return result['sequence_no']


def get_doc_from_store(mongoid):
    store_url = "{0}/responses/{1}".format(SDX_STORE_URL, mongoid)
    response = remote_call(store_url)

    if not response_ok(response):
        return None

    result = response.json()
    return result['survey_response']
