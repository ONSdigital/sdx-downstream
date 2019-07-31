import json
import unittest

from app.processors.transform_processor import TransformProcessor
from app.helpers.sdxftp import SDXFTP
from tests.test_data import cora_survey, cord_survey, common_software_survey

ftpconn = SDXFTP("", "", "")


class TestTransformProcessor(unittest.TestCase):

    def test_cora_endpoint_selected_for_cora_survey(self):
        survey = json.loads(cora_survey)

        sut = TransformProcessor(survey, ftpconn)

        self.assertEqual(sut._endpoint_name, 'cora')

    def test_cora_endpoint_selected_for_cord_survey(self):
        survey = json.loads(cord_survey)

        sut = TransformProcessor(survey, ftpconn)

        self.assertEqual(sut._endpoint_name, 'cord')

    def test_cora_endpoint_selected_for_common_software_survey(self):
        survey = json.loads(common_software_survey)

        sut = TransformProcessor(survey, ftpconn)

        self.assertEqual(sut._endpoint_name, 'common-software')
