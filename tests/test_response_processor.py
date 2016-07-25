import unittest
import logging
import json
from app import settings
from unittest.mock import MagicMock
from structlog import wrap_logger
from app.response_processor import ResponseProcessor, get_ftp_folder, is_census
from tests.test_data import survey_census, survey_023

logger = wrap_logger(logging.getLogger(__name__))


class TestResponseProcessor(unittest.TestCase):

    def setUp(self):
        self.survey = json.loads(survey_023)
        self.census = json.loads(survey_census)

    def add_tx(self):
        self.survey["tx_id"] = "0f534ffc-9442-414c-b39f-a756b4adc6cb"

    def add_heartbeat(self):
        self.survey["heartbeat"] = True

    def test_store_response_failure(self):
        rp = ResponseProcessor(logger)
        rp.get_doc_from_store = MagicMock(return_value=False)
        response = rp.process("some_made_up_id")

        rp.get_doc_from_store.assert_called_with("some_made_up_id")

        self.assertFalse(response)

    def test_store_response_success(self):
        # test without tx_id
        rp = ResponseProcessor(logger)
        rp.get_doc_from_store = MagicMock(return_value=self.survey)
        rp.get_sequence_no = MagicMock(return_value=False)

        response = rp.process("some_made_up_id")

        self.assertFalse(response)

        # with tx_id
        self.add_tx()
        rp = ResponseProcessor(logger)
        rp.get_doc_from_store = MagicMock(return_value=self.survey)
        rp.get_sequence_no = MagicMock(return_value=False)

        response = rp.process("some_made_up_id")

        self.assertFalse(response)

    def test_sequence_response_failure(self):
        rp = ResponseProcessor(logger)
        rp.get_doc_from_store = MagicMock(return_value=self.survey)
        rp.get_sequence_no = MagicMock(return_value=False)

        response = rp.process("some_made_up_id")

        self.assertFalse(response)

    def test_sequence_response_success(self):
        rp = ResponseProcessor(logger)
        rp.get_doc_from_store = MagicMock(return_value=self.survey)
        rp.get_sequence_no = MagicMock(return_value=1)
        rp.transform_cs = MagicMock(return_value=False)

        response = rp.process("some_made_up_id")

        self.assertFalse(response)
        rp.transform_cs.assert_called_with(1, self.survey)

    def test_transform_cs_failure(self):
        fake_zip = {"content": "some-random-content"}

        rp = ResponseProcessor(logger)
        rp.get_doc_from_store = MagicMock(return_value=self.survey)
        rp.get_sequence_no = MagicMock(return_value=1)
        rp.transform_cs = MagicMock(return_value=fake_zip)
        rp.process_zip = MagicMock(return_value=False)

        response = rp.process("some_made_up_id")

        rp.transform_cs.assert_called_with(1, self.survey)
        rp.process_zip.assert_called_with(settings.FTP_FOLDER, fake_zip)
        self.assertFalse(response)

    def test_transform_reponse_success(self):
        fake_zip = {"content": "some-random-content"}

        rp = ResponseProcessor(logger)
        rp.get_doc_from_store = MagicMock(return_value=self.survey)
        rp.get_sequence_no = MagicMock(return_value=1)
        rp.transform_cs = MagicMock(return_value=fake_zip)
        rp.process_zip = MagicMock(return_value=True)

        response = rp.process("some_made_up_id")

        rp.transform_cs.assert_called_with(1, self.survey)
        rp.process_zip.assert_called_with(settings.FTP_FOLDER, fake_zip)
        self.assertTrue(response)

    def test_transform_xml_failure(self):
        fake_xml = {"content": "<xml>some-random-content</xml>"}

        rp = ResponseProcessor(logger)
        rp.get_doc_from_store = MagicMock(return_value=self.census)
        rp.get_sequence_no = MagicMock(return_value=1)
        rp.transform_xml = MagicMock(return_value=fake_xml)
        rp.notify_queue = MagicMock(return_value=False)

        response = rp.process("some_made_up_id")
        rp.notify_queue.assert_called_with(fake_xml)
        self.assertFalse(response)

    def test_transform_xml_success(self):
        fake_xml = {"content": "<xml>some-random-content</xml>"}

        rp = ResponseProcessor(logger)
        rp.get_doc_from_store = MagicMock(return_value=self.census)
        rp.get_sequence_no = MagicMock(return_value=1)
        rp.transform_xml = MagicMock(return_value=fake_xml)
        rp.notify_queue = MagicMock(return_value=True)

        response = rp.process("some_made_up_id")
        rp.notify_queue.assert_called_with(fake_xml)
        self.assertTrue(response)

    def test_get_ftp_folder_no_heartbeat(self):
        folder = get_ftp_folder(self.survey)
        self.assertEqual(folder, settings.FTP_FOLDER)

    def test_get_ftp_folder_heartbeat_false(self):
        self.add_heartbeat()
        self.survey["heartbeat"] = False
        folder = get_ftp_folder(self.survey)
        self.assertEqual(folder, settings.FTP_FOLDER)

    def test_get_ftp_folder_heartbeat_true(self):
        self.add_heartbeat()
        folder = get_ftp_folder(self.survey)
        self.assertEqual(folder, settings.FTP_HEARTBEAT_FOLDER)

    def test_is_census_false(self):
        result = is_census(self.survey)
        self.assertEqual(result, False)

    def test_is_census_true(self):
        result = is_census(self.census)
        self.assertEqual(result, True)
