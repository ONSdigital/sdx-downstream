import unittest
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
