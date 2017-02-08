import unittest
from requests import Response
from app.helpers import request_helper


class TestSurveyProcessor(unittest.TestCase):

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
