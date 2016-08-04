import unittest
import json
import logging
from structlog import wrap_logger
from app.processors.census_processor import CensusProcessor
from tests.test_data import ce_census_survey

logger = wrap_logger(logging.getLogger(__name__))


class TestCensusProcessor(unittest.TestCase):

    def setUp(self):
        survey = json.loads(ce_census_survey)
        self.processor = CensusProcessor(logger, survey)
