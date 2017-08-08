import json
import unittest

import logging
import mock
from structlog import wrap_logger

from app.processors.message_processor import MessageProcessor
from tests.test_data import common_software_survey


class TestResponseProcessor(unittest.TestCase):

    def setUp(self):
        self.logger = wrap_logger(logging.getLogger(__name__))
        self.message_processor = MessageProcessor(logger=self.logger)

    def test_message_processor_logging(self):

        with mock.patch('app.processors.message_processor.get_doc_from_store') as get_doc_mock:
            get_doc_mock.return_value = json.loads(common_software_survey)
            with mock.patch('app.processors.common_software_processor.CommonSoftwareProcessor.process') as csp_mock:
                with self.assertLogs(level='INFO') as cm:

                    csp_mock.return_value = None

                    self.message_processor.process("0f534ffc-9442-414c-b39f-a756b4adc6cb",
                                                   "0f534ffc-9442-414c-b39f-a756b4adc6cb")

            self.assertIn("Received message", cm[0][0].message)
            self.assertIn("Processed successfully", cm[0][1].message)
