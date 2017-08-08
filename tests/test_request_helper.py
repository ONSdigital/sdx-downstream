import unittest
from requests import Response
from app.helpers import request_helper
from sdc.rabbit.exceptions import QuarantinableError, RetryableError


class TestSurveyProcessor(unittest.TestCase):

    def test_response_ok_200_return_true(self):
        response = Response()
        response.status_code = 200
        result = request_helper.response_ok(response)
        self.assertEqual(result, True)

    def test_response_ok_400_raise_bad_request_error(self):
        response = Response()
        response.status_code = 400
        with self.assertRaises(QuarantinableError):
            request_helper.response_ok(response)

    def test_response_ok_500_raise_retryable_error(self):
        response = Response()
        response.status_code = 500
        with self.assertRaises(RetryableError):
            request_helper.response_ok(response)

    def test_response_ok_404_raises_not_found_error(self):
        response = Response()
        response.status_code = 404
        with self.assertRaises(QuarantinableError):
            request_helper.response_ok(response)

    def test_service_name_return_responses(self):
        url = "www.testing.test/responses/12345"
        service = request_helper.service_name(url)
        self.assertEqual(service, 'SDX_STORE')

    def test_service_name_return_sequence(self):
        url = "www.testing.test/sequence"
        service = request_helper.service_name(url)
        self.assertEqual(service, 'SDX_SEQUENCE')

    def test_service_name_return_common_software(self):
        url = "www.testing.test/common-software/12345"
        service = request_helper.service_name(url)
        self.assertEqual(service, 'SDX_TRANSFORM_CS')

    def test_service_name_return_none(self):
        url = "www.testing.test/test/12345"
        service = request_helper.service_name(url)
        self.assertEqual(service, None)

    def test_service_name_url_none(self):
        url = None
        service = request_helper.service_name(url)
        self.assertEqual(service, None)
