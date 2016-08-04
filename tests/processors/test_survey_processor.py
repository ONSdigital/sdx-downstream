import unittest
import logging
import json
from structlog import wrap_logger
from app.processors.survey_processor import SurveyProcessor
from tests.test_data import common_software_survey

logger = wrap_logger(logging.getLogger(__name__))


class TestSurveyProcessor(unittest.TestCase):

    def setUp(self):
        survey = json.loads(common_software_survey)
        self.processor = SurveyProcessor(logger, survey)

    def test_process_should_raise_not_implemented_error(self):
        self.assertRaises(NotImplementedError, self.processor.process)

    def test_tx_id_should_be_set(self):
        self.assertIsNotNone(self.processor.tx_id)
