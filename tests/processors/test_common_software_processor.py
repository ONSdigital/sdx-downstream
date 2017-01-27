import unittest
from unittest.mock import MagicMock
import json
import logging
from app import settings
from structlog import wrap_logger
from app.processors.common_software_processor import CommonSoftwareProcessor
from tests.test_data import common_software_survey

logger = wrap_logger(logging.getLogger(__name__))


class TestCommonSoftwareProcessor(unittest.TestCase):

    def setUp(self):
        survey = json.loads(common_software_survey)
        self.processor = CommonSoftwareProcessor(logger, survey)

    def test_tx_id_should_be_set(self):
        self.assertIsNotNone(self.processor.tx_id)

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

    # FTP FOLDER
    def test_get_ftp_folder_no_heartbeat(self):
        survey = json.loads(common_software_survey)
        folder = self.processor.get_ftp_folder(survey)
        self.assertEqual(folder, settings.FTP_FOLDER)

    def test_get_ftp_folder_heartbeat_false(self):
        survey = json.loads(common_software_survey)
        survey["heartbeat"] = False
        folder = self.processor.get_ftp_folder(survey)
        self.assertEqual(folder, settings.FTP_FOLDER)

    def test_get_ftp_folder_heartbeat_true(self):
        survey = json.loads(common_software_survey)
        survey["heartbeat"] = True
        folder = self.processor.get_ftp_folder(survey)
        self.assertEqual(folder, settings.FTP_HEARTBEAT_FOLDER)
