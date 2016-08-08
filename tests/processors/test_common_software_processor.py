import unittest
from unittest.mock import MagicMock
import json
import logging
from structlog import wrap_logger
from app.processors.common_software_processor import CommonSoftwareProcessor
from tests.test_data import common_software_survey

logger = wrap_logger(logging.getLogger(__name__))


class TestCommonSoftwareProcessor(unittest.TestCase):

    def setUp(self):
        survey = json.loads(common_software_survey)
        self.processor = CommonSoftwareProcessor(logger, survey)

    def test_transform_failure(self):
        self.processor.transform = MagicMock(return_value=None)
        result = self.processor.process()
        self.assertFalse(result)

    def test_process_failure(self):
        self.processor.transform = MagicMock(return_value="success")
        self.processor.deliver_zip = MagicMock(return_value=False)
        result = self.processor.process()
        self.assertFalse(result)

    def test_process_success(self):
        self.processor.transform = MagicMock(return_value="success")
        self.processor.deliver_zip = MagicMock(return_value=True)
        result = self.processor.process()
        self.assertTrue(result)
