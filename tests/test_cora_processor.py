import json
import logging

import structlog
from structlog.stdlib import LoggerFactory
from structlog.threadlocal import wrap_dict
import unittest
from unittest.mock import MagicMock

from app import settings
from app.helpers.sdxftp import SDXFTP
from app.processors.transform_processor import TransformProcessor
from tests.test_data import cora_survey
from tests.processor_test_base import ProcessorTestBase

ftpconn = SDXFTP("", "", "")


class TestCoraProcessor(unittest.TestCase, ProcessorTestBase):

    def setUp(self):
        logging.basicConfig(format=settings.LOGGING_FORMAT,
                            datefmt="%Y-%m-%dT%H:%M:%S",
                            level=settings.LOGGING_LEVEL)

        logging.getLogger('sdc.rabbit').setLevel(logging.INFO)

        structlog.configure(logger_factory=LoggerFactory(), context_class=wrap_dict(dict))
        survey = json.loads(cora_survey)
        self.processor = TransformProcessor(survey, ftpconn)
        self.processor.ftp.unzip_and_deliver = MagicMock(return_value=True)

    def test_if_no_metadata_error_is_logged(self):
        survey = {"a key": "a value", "survey_id": "a_survey_id"}
        with self.assertLogs(level='ERROR') as cm:
            self.processor = TransformProcessor(survey, ftpconn)
        self.assertIn("Failed to get metadata", cm[0][0].message)
