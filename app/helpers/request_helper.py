from app import settings
from requests.packages.urllib3.exceptions import MaxRetryError
from app.settings import logger


def remote_call(url, json=None):
    try:
        logger.info("Calling service", request_url=url)
        response = None

        if json:
            response = settings.session.post(url, json=json)
        else:
            response = settings.session.get(url)

        return response

    except MaxRetryError:
        logger.error("Max retries exceeded (5)", request_url=url)
        return False


def response_ok(response):
    if response.status_code == 200:
        logger.info("Returned from service", request_url=response.url, status_code=response.status_code)
        return True

    else:
        logger.error("Returned from service", request_url=response.url, status_code=response.status_code)
        return False


def get_sequence_no():
    sequence_url = settings.SDX_SEQUENCE_URL + "/sequence"
    response = remote_call(sequence_url)
    if not response_ok(response):
        return None

    result = response.json()
    return result['sequence_no']


def get_doc_from_store(mongoid):
    store_url = settings.SDX_STORE_URL + "/responses/" + mongoid
    response = remote_call(store_url)

    if not response_ok(response):
        return None

    result = response.json()
    return result['survey_response']
