import unittest
import logging
import json
from app import settings
from unittest.mock import MagicMock
from structlog import wrap_logger
from app.response_processor import ResponseProcessor, get_ftp_folder, is_census_type
from tests.test_data import survey_ce_census, survey_hh_census, survey_with_tx_id

logger = wrap_logger(logging.getLogger(__name__))


class TestResponseProcessor(unittest.TestCase):

    def test_store_response_failure(self):
        rp = ResponseProcessor(logger)
        rp.get_doc_from_store = MagicMock(return_value=False)
        response = rp.process("some_made_up_id")

        rp.get_doc_from_store.assert_called_with("some_made_up_id")

        self.assertFalse(response)

    def test_store_response_success(self):
        survey = json.loads(survey_with_tx_id)

        rp = ResponseProcessor(logger)
        rp.get_doc_from_store = MagicMock(return_value=survey)
        rp.get_sequence_no = MagicMock(return_value=False)

        response = rp.process("some_made_up_id")

        self.assertFalse(response)

    def test_store_response_success_no_tx_id(self):
        survey = json.loads(survey_with_tx_id)
        del survey["tx_id"]

        rp = ResponseProcessor(logger)
        rp.get_doc_from_store = MagicMock(return_value=survey)
        rp.get_sequence_no = MagicMock(return_value=False)

        response = rp.process("some_made_up_id")

        self.assertFalse(response)

    def test_sequence_response_failure(self):
        survey = json.loads(survey_with_tx_id)

        rp = ResponseProcessor(logger)
        rp.get_doc_from_store = MagicMock(return_value=survey)
        rp.get_sequence_no = MagicMock(return_value=False)

        response = rp.process("some_made_up_id")

        self.assertFalse(response)

    def test_sequence_response_success(self):
        survey = json.loads(survey_with_tx_id)

        rp = ResponseProcessor(logger)
        rp.get_doc_from_store = MagicMock(return_value=survey)
        rp.get_sequence_no = MagicMock(return_value=1)
        rp.transform_cs = MagicMock(return_value=False)

        response = rp.process("some_made_up_id")

        self.assertFalse(response)
        rp.transform_cs.assert_called_with(1, survey)

    def test_transform_cs_failure(self):
        survey = json.loads(survey_with_tx_id)
        fake_zip = {"content": "some-random-content"}

        rp = ResponseProcessor(logger)
        rp.get_doc_from_store = MagicMock(return_value=survey)
        rp.get_sequence_no = MagicMock(return_value=1)
        rp.transform_cs = MagicMock(return_value=fake_zip)
        rp.process_zip = MagicMock(return_value=False)

        response = rp.process("some_made_up_id")

        rp.transform_cs.assert_called_with(1, survey)
        rp.process_zip.assert_called_with(settings.FTP_FOLDER, fake_zip)
        self.assertFalse(response)

    def test_transform_reponse_success(self):
        survey = json.loads(survey_with_tx_id)
        fake_zip = {"content": "some-random-content"}

        rp = ResponseProcessor(logger)
        rp.get_doc_from_store = MagicMock(return_value=survey)
        rp.get_sequence_no = MagicMock(return_value=1)
        rp.transform_cs = MagicMock(return_value=fake_zip)
        rp.process_zip = MagicMock(return_value=True)

        response = rp.process("some_made_up_id")

        rp.transform_cs.assert_called_with(1, survey)
        rp.process_zip.assert_called_with(settings.FTP_FOLDER, fake_zip)
        self.assertTrue(response)

    def test_transform_ce_xml_failure(self):
        census = json.loads(survey_ce_census)
        fake_xml = {"content": "<xml>some-random-content</xml>"}

        rp = ResponseProcessor(logger)
        rp.get_doc_from_store = MagicMock(return_value=census)
        rp.get_sequence_no = MagicMock(return_value=1)
        rp.transform_xml = MagicMock(return_value=fake_xml)
        rp.notify_queue = MagicMock(return_value=False)

        response = rp.process("some_made_up_id")
        rp.notify_queue.assert_called_with(fake_xml)
        self.assertFalse(response)

    def test_transform_ce_xml_success(self):
        census = json.loads(survey_ce_census)
        fake_xml = {"content": "<xml>some-random-content</xml>"}

        rp = ResponseProcessor(logger)
        rp.get_doc_from_store = MagicMock(return_value=census)
        rp.get_sequence_no = MagicMock(return_value=1)
        rp.transform_xml = MagicMock(return_value=fake_xml)
        rp.notify_queue = MagicMock(return_value=True)

        response = rp.process("some_made_up_id")
        rp.notify_queue.assert_called_with(fake_xml)
        self.assertTrue(response)

    def test_transform_hh_xml_failure(self):
        census = json.loads(survey_hh_census)
        fake_xml = {"content": "<xml>some-random-content</xml>"}

        rp = ResponseProcessor(logger)
        rp.get_doc_from_store = MagicMock(return_value=census)
        rp.get_sequence_no = MagicMock(return_value=1)
        rp.transform_xml = MagicMock(return_value=fake_xml)
        rp.notify_queue = MagicMock(return_value=False)

        response = rp.process("some_made_up_id")
        rp.notify_queue.assert_called_with(fake_xml)
        self.assertFalse(response)

    def test_transform_hh_xml_success(self):
        census = json.loads(survey_hh_census)
        fake_xml = {"content": "<xml>some-random-content</xml>"}

        rp = ResponseProcessor(logger)
        rp.get_doc_from_store = MagicMock(return_value=census)
        rp.get_sequence_no = MagicMock(return_value=1)
        rp.transform_xml = MagicMock(return_value=fake_xml)
        rp.notify_queue = MagicMock(return_value=True)

        response = rp.process("some_made_up_id")
        rp.notify_queue.assert_called_with(fake_xml)
        self.assertTrue(response)

    def test_get_ftp_folder_no_heartbeat(self):
        survey = json.loads(survey_with_tx_id)

        folder = get_ftp_folder(survey)
        self.assertEqual(folder, settings.FTP_FOLDER)

    def test_get_ftp_folder_heartbeat_false(self):
        survey = json.loads(survey_with_tx_id)
        survey["heartbeat"] = False

        folder = get_ftp_folder(survey)
        self.assertEqual(folder, settings.FTP_FOLDER)

    def test_get_ftp_folder_heartbeat_true(self):
        survey = json.loads(survey_with_tx_id)
        survey["heartbeat"] = True

        folder = get_ftp_folder(survey)
        self.assertEqual(folder, settings.FTP_HEARTBEAT_FOLDER)

    def test_is_census_false(self):
        survey = json.loads(survey_with_tx_id)
        result = is_census_type(survey, settings.CENSUS_CE_IDENTIFIER)
        self.assertEqual(result, False)

    def test_ce_is_census_true(self):
        census = json.loads(survey_ce_census)
        result = is_census_type(census, settings.CENSUS_CE_IDENTIFIER)
        self.assertEqual(result, True)

    def test_hh_is_census_true(self):
        census = json.loads(survey_hh_census)
        logger.debug(settings.CENSUS_HH_IDENTIFIER)
        result = is_census_type(census, settings.CENSUS_HH_IDENTIFIER)
        self.assertEqual(result, True)
