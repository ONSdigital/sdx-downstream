import unittest
import logging
import json
from unittest.mock import MagicMock
from app.response_processor import ResponseProcessor
from structlog import wrap_logger

logger = wrap_logger(logging.getLogger(__name__))


class TestResponseProcessor(unittest.TestCase):
    RESPONSE_WITHOUT_TX = '''{
            "metadata": {
              "user_id": "789473423",
              "ru_ref": "12345678901A"
            }
        }'''

    RESPONSE_WITH_TX = '''{
            "tx_id": "0f534ffc-9442-414c-b39f-a756b4adc6cb",
            "metadata": {
              "user_id": "789473423",
              "ru_ref": "12345678901A"
            }
        }'''

    XML_RESPONSE = '''{
            "file-type": "xml",
            "tx_id": "0f534ffc-9442-414c-b39f-a756b4adc6cb",
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
        fake_response = json.loads(self.RESPONSE_WITH_TX)

        rp = ResponseProcessor(logger)
        rp.get_doc_from_store = MagicMock(return_value=fake_response)
        rp.get_sequence_no = MagicMock(return_value=False)

        response = rp.process("some_made_up_id")

        self.assertFalse(response)

        # Also test without the tx_id
        fake_response = json.loads(self.RESPONSE_WITHOUT_TX)

        rp = ResponseProcessor(logger)
        rp.get_doc_from_store = MagicMock(return_value=fake_response)
        rp.get_sequence_no = MagicMock(return_value=False)

        response = rp.process("some_made_up_id")

        self.assertFalse(response)

    def test_sequence_response_failure(self):
        fake_response = json.loads(self.RESPONSE_WITH_TX)

        rp = ResponseProcessor(logger)
        rp.get_doc_from_store = MagicMock(return_value=fake_response)
        rp.get_sequence_no = MagicMock(return_value=False)

        response = rp.process("some_made_up_id")

        self.assertFalse(response)

    def test_sequence_response_success(self):
        fake_response = json.loads(self.RESPONSE_WITH_TX)

        rp = ResponseProcessor(logger)
        rp.get_doc_from_store = MagicMock(return_value=fake_response)
        rp.get_sequence_no = MagicMock(return_value=1)
        rp.transform_cs = MagicMock(return_value=False)

        response = rp.process("some_made_up_id")

        self.assertFalse(response)
        rp.transform_cs.assert_called_with(1, fake_response)

    def test_transform_cs_failure(self):
        fake_response = json.loads(self.RESPONSE_WITH_TX)

        fake_zip = {"content": "some-random-content"}

        rp = ResponseProcessor(logger)
        rp.get_doc_from_store = MagicMock(return_value=fake_response)
        rp.get_sequence_no = MagicMock(return_value=1)
        rp.transform_cs = MagicMock(return_value=fake_zip)
        rp.process_zip = MagicMock(return_value=False)

        response = rp.process("some_made_up_id")

        rp.transform_cs.assert_called_with(1, fake_response)
        rp.process_zip.assert_called_with(fake_zip)
        self.assertFalse(response)

    def test_transform_reponse_success(self):
        fake_response = json.loads(self.RESPONSE_WITH_TX)

        fake_zip = {"content": "some-random-content"}

        rp = ResponseProcessor(logger)
        rp.get_doc_from_store = MagicMock(return_value=fake_response)
        rp.get_sequence_no = MagicMock(return_value=1)
        rp.transform_cs = MagicMock(return_value=fake_zip)
        rp.process_zip = MagicMock(return_value=True)

        response = rp.process("some_made_up_id")

        rp.transform_cs.assert_called_with(1, fake_response)
        rp.process_zip.assert_called_with(fake_zip)
        self.assertTrue(response)

    def test_transform_xml_failure(self):
        fake_response = json.loads(self.XML_RESPONSE)

        fake_xml = {"content": "<xml>some-random-content</xml>"}

        rp = ResponseProcessor(logger)
        rp.get_doc_from_store = MagicMock(return_value=fake_response)
        rp.get_sequence_no = MagicMock(return_value=1)
        rp.transform_xml = MagicMock(return_value=fake_xml)
        rp.notify_queue = MagicMock(return_value=False)

        response = rp.process("some_made_up_id")
        rp.notify_queue.assert_called_with(fake_xml)
        self.assertFalse(response)

    def test_transform_xml_success(self):
        fake_response = json.loads(self.XML_RESPONSE)

        fake_xml = {"content": "<xml>some-random-content</xml>"}

        rp = ResponseProcessor(logger)
        rp.get_doc_from_store = MagicMock(return_value=fake_response)
        rp.get_sequence_no = MagicMock(return_value=1)
        rp.transform_xml = MagicMock(return_value=fake_xml)
        rp.notify_queue = MagicMock(return_value=True)

        response = rp.process("some_made_up_id")
        rp.notify_queue.assert_called_with(fake_xml)
        self.assertTrue(response)
