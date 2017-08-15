import unittest
import mock
from unittest.mock import MagicMock
import json
import logging
from structlog import wrap_logger
from app.processors.common_software_processor import CommonSoftwareProcessor
from tests.test_data import common_software_survey
from requests import Response
from app.helpers.sdxftp import SDXFTP
from sdc.rabbit.exceptions import QuarantinableError, RetryableError

logger = wrap_logger(logging.getLogger(__name__))
ftpconn = SDXFTP(logger, "", "", "")


class TestCommonSoftwareProcessor(unittest.TestCase):

    def setUp(self):
        survey = json.loads(common_software_survey)
        self.processor = CommonSoftwareProcessor(logger, survey, ftpconn)
        self.processor.ftp.unzip_and_deliver = MagicMock(return_value=True)

    def _get_response(self):
        response = Response()
        response.status_code = 200
        response._content = b'Some content'
        return response

    def test_transform(self):
        with mock.patch('app.processors.common_software_processor.get_sequence_no') as seq_mock:
            seq_mock.return_value = '1001'
            response = self._get_response()

            with mock.patch('app.processors.common_software_processor.remote_call') as call_mock:

                # 500 something ary
                response.status_code = 500
                call_mock.return_value = response
                with self.assertRaises(RetryableError):
                    self.processor.process()

                # 400 bad data sent
                response.status_code = 400
                call_mock.return_value = response
                with self.assertRaises(QuarantinableError):
                    self.processor.process()

                # 200 and content
                response.status_code = 200
                call_mock.return_value = response
                self.processor.process()

                # 200 and missing content
                response._content = None
                call_mock.return_value = response
                with self.assertRaises(QuarantinableError):
                    self.processor.process()

    def test_sequence(self):
        with mock.patch('app.processors.common_software_processor.get_sequence_no') as seq_mock:

            response = self._get_response()
            with mock.patch('app.processors.common_software_processor.remote_call') as call_mock:
                call_mock.return_value = response

                # Good return
                seq_mock.return_value = '1001'
                self.processor.process()

                # Call issue
                seq_mock.return_value = None
                with self.assertRaises(RetryableError):
                    self.processor.process()

    def test_ftp(self):
        with mock.patch('app.processors.common_software_processor.get_sequence_no') as seq_mock:
            seq_mock.return_value = '1001'

            response = self._get_response()
            with mock.patch('app.processors.common_software_processor.remote_call') as call_mock:
                call_mock.return_value = response

                # Good deliver
                self.processor.ftp.unzip_and_deliver = MagicMock(return_value=True)
                self.processor.process()

                # Failed deliver
                self.processor.ftp.unzip_and_deliver = MagicMock(return_value=False)
                with self.assertRaises(RetryableError):
                    self.processor.process()
