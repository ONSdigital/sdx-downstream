import json
import mock
import logging
import unittest

import structlog
from structlog.stdlib import LoggerFactory
from structlog.threadlocal import wrap_dict

from app import settings
from app.processors.message_processor import MessageProcessor
from tests.test_data import common_software_survey, cora_survey, feedback_decrypted


id_tag = '{"tx_id":"0f534ffc-9442-414c-b39f-a756b4adc6cb","is_feedback":false}'
feedback_id_tag = '{"tx_id": "0f534ffc-9442-414c-b39f-a756b4adc6cb","is_feedback":true,"feedback_id":123}'
tx_id = "0f534ffc-9442-414c-b39f-a756b4adc6cb"
feedback = json.loads(feedback_decrypted)


class TestMessageProcessor(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(format=settings.LOGGING_FORMAT,
                            datefmt="%Y-%m-%dT%H:%M:%S",
                            level=settings.LOGGING_LEVEL)

        logging.getLogger('sdc.rabbit').setLevel(logging.INFO)

        structlog.configure(logger_factory=LoggerFactory(), context_class=wrap_dict(dict))
        self.message_processor = MessageProcessor()

    def test_message_processor_logging_common_software(self):

        with mock.patch('app.processors.message_processor.get_doc_from_store') as get_doc_mock:
            get_doc_mock.return_value = json.loads(common_software_survey)
            with mock.patch('app.processors.transform_processor.TransformProcessor.process') as csp_mock:
                with self.assertLogs(level='INFO') as cm:

                    csp_mock.return_value = None

                    self.message_processor.process(id_tag, tx_id)

            self.assertIn("Received message", cm[0][0].message)
            self.assertIn("Processed successfully", cm[0][1].message)

    def test_message_processor_logging_cora(self):

        with mock.patch('app.processors.message_processor.get_doc_from_store') as get_doc_mock:
            get_doc_mock.return_value = json.loads(cora_survey)
            with mock.patch('app.processors.transform_processor.TransformProcessor.process') as cora_mock:
                with self.assertLogs(level='INFO') as cm:

                    cora_mock.return_value = None

                    self.message_processor.process(id_tag, tx_id)

            self.assertIn("Received message", cm[0][0].message)
            self.assertIn("Processed successfully", cm[0][1].message)

    def test_message_processor_logs_error_if_KeyError_raised(self):

        with mock.patch('app.processors.message_processor.get_doc_from_store') as get_doc_mock:
            get_doc_mock.return_value = json.loads(cora_survey)
            with mock.patch('app.processors.transform_processor.TransformProcessor.process') as cora_mock:
                with self.assertLogs(level='INFO') as cm:

                    cora_mock.side_effect = KeyError

                    self.message_processor.process(id_tag, tx_id)

            self.assertIn("Received message", cm[0][0].message)
            self.assertIn("No survey ID in document", cm[0][1].message)

    def test_msg_is_used_if_tx_id_is_none(self):

        with mock.patch('app.processors.message_processor.get_doc_from_store') as get_doc_mock:
            get_doc_mock.return_value = json.loads(cora_survey)
            with mock.patch('app.processors.transform_processor.TransformProcessor.process'):
                with self.assertLogs(level='INFO') as cm:
                    self.message_processor.process(id_tag, None)

            self.assertIn("tx_id=0f534ffc-9442-414c-b39f-a756b4adc6cb", cm[0][0].message)

    def test_message_processor_logging_feedback(self):

        with mock.patch('app.processors.message_processor.get_feedback_from_store') as get_feedback_mock:
            get_feedback_mock.return_value = json.loads(feedback_decrypted)
            with mock.patch('app.helpers.sdxftp.SDXFTP.deliver_binary'):
                with self.assertLogs(level='INFO') as cm:
                    self.message_processor.process(feedback_id_tag, tx_id)

            self.assertIn("Received message", cm[0][0].message)
            self.assertIn("Processed successfully", cm[0][1].message)

    def test_msg_is_used_if_tx_id_is_none_feedback(self):

        with mock.patch('app.processors.message_processor.get_feedback_from_store') as get_feedback_mock:
            get_feedback_mock.return_value = json.loads(feedback_decrypted)
            with mock.patch('app.helpers.sdxftp.SDXFTP.deliver_binary'):
                with self.assertLogs(level='INFO') as cm:
                    self.message_processor.process(feedback_id_tag, None)

            self.assertIn("tx_id=0f534ffc-9442-414c-b39f-a756b4adc6cb", cm[0][0].message)

    def test_message_processor_feedback_logs_error_if_KeyError_raised(self):

        with mock.patch('app.processors.message_processor.get_feedback_from_store') as get_feedback_mock:
            get_feedback_mock.return_value = json.loads(feedback_decrypted)
            with mock.patch('app.helpers.sdxftp.SDXFTP.deliver_binary') as feedback_mock:
                with self.assertLogs(level='INFO') as cm:

                    feedback_mock.side_effect = KeyError

                    self.message_processor.process(feedback_id_tag, tx_id)

            self.assertIn("Received message", cm[0][0].message)
            self.assertIn("No survey ID in document", cm[0][1].message)

    def test_message_processor_feedback_logging_common_software(self):

        with mock.patch('app.processors.message_processor.get_feedback_from_store') as get_feedback_mock:
            get_feedback_mock.return_value = json.loads(feedback_decrypted)
            with mock.patch('app.helpers.sdxftp.SDXFTP.deliver_binary') as csp_mock:
                with self.assertLogs(level='INFO') as cm:

                    csp_mock.return_value = None

                    self.message_processor.process(feedback_id_tag, tx_id)

            self.assertIn("Received message", cm[0][0].message)
            self.assertIn("Processed successfully", cm[0][1].message)
