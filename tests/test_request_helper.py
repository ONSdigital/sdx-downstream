import unittest
from requests import Response
from app.helpers import request_helper


class TestSurveyProcessor(unittest.TestCase):

    def test_response_None(self):
        response = None
        result = request_helper.response_ok(response)
        self.assertEqual(result, False)

    def test_response_ok_200_return_true(self):
        response = Response()
        response.status_code = 200
        result = request_helper.response_ok(response)
        self.assertEqual(result, True)

    def test_response_ok_400_return_false(self):
        response = Response()
        response.status_code = 400
        result = request_helper.response_ok(response)
        self.assertEqual(result, False)

    def test_response_ok_500_return_false(self):
        response = Response()
        response.status_code = 500
        result = request_helper.response_ok(response)
        self.assertEqual(result, False)

    def test_url_splitter_return_responses(self):
        url = "www.testing.test/responses/12345"
        service = request_helper.url_splitter(url)
        self.assertEqual(service, 'responses')

    def test_url_splitter_return_rsequence(self):
        url = "www.testing.test/sequence"
        service = request_helper.url_splitter(url)
        self.assertEqual(service, 'sequence')

    def test_url_splitter_return_none(self):
        url = "www.testing.test/test/12345"
        service = request_helper.url_splitter(url)
        self.assertEqual(service, None)

    def test_url_splitter_url_none(self):
        url = None
        service = request_helper.url_splitter(url)
        self.assertEqual(service, None)
