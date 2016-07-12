import unittest
import logging
import json
from unittest.mock import MagicMock
from app import ResponseProcessor
logger = logging.getLogger(__name__)


class TestResponseProcessor(unittest.TestCase):
    METADATA_RESPONSE = '''{
            "metadata": {
              "user_id": "789473423",
              "ru_ref": "12345678901A"
            }
        }'''

    def test_store_response_failure(self):
        rp = ResponseProcessor(logger)
        rp.get_doc_from_store = MagicMock(return_value=False)
        response = rp.process("some_made_up_id")

        rp.get_doc_from_store.assert_called_with("some_made_up_id")
        self.assertFalse(response)

    def test_store_response_success(self):
        fake_response = json.loads(self.METADATA_RESPONSE)

        rp = ResponseProcessor(logger)
        rp.get_doc_from_store = MagicMock(return_value=fake_response)
        rp.get_sequence_no = MagicMock(return_value=False)

        response = rp.process("some_made_up_id")

        self.assertFalse(response)

    def test_sequence_response_failure(self):
        fake_response = json.loads(self.METADATA_RESPONSE)

        rp = ResponseProcessor(logger)
        rp.get_doc_from_store = MagicMock(return_value=fake_response)
        rp.get_sequence_no = MagicMock(return_value=False)

        response = rp.process("some_made_up_id")

        self.assertFalse(response)

    def test_sequence_response_success(self):
        fake_response = json.loads(self.METADATA_RESPONSE)

        rp = ResponseProcessor(logger)
        rp.get_doc_from_store = MagicMock(return_value=fake_response)
        rp.get_sequence_no = MagicMock(return_value=1)
        rp.transform_response = MagicMock(return_value=False)

        response = rp.process("some_made_up_id")

        self.assertFalse(response)
        rp.transform_response.assert_called_with(1, fake_response)

    def test_transform_response_failure(self):
        fake_response = json.loads(self.METADATA_RESPONSE)

        fake_zip = {"content": "some-random-content"}

        rp = ResponseProcessor(logger)
        rp.get_doc_from_store = MagicMock(return_value=fake_response)
        rp.get_sequence_no = MagicMock(return_value=1)
        rp.transform_response = MagicMock(return_value=fake_zip)
        rp.process_zip = MagicMock(return_value=False)

        response = rp.process("some_made_up_id")

        rp.transform_response.assert_called_with(1, fake_response)
        rp.process_zip.assert_called_with(fake_zip)
        self.assertFalse(response)

    def test_transform_reponse_success(self):
        fake_response = json.loads(self.METADATA_RESPONSE)

        fake_zip = {"content": "some-random-content"}

        rp = ResponseProcessor(logger)
        rp.get_doc_from_store = MagicMock(return_value=fake_response)
        rp.get_sequence_no = MagicMock(return_value=1)
        rp.transform_response = MagicMock(return_value=fake_zip)
        rp.process_zip = MagicMock(return_value=True)

        response = rp.process("some_made_up_id")

        rp.transform_response.assert_called_with(1, fake_response)
        rp.process_zip.assert_called_with(fake_zip)
        self.assertTrue(response)
