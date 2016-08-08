import unittest
import json
from app import settings
from app.helpers import ftp_helper
from tests.test_data import common_software_survey


class TestSurveyProcessor(unittest.TestCase):

    def test_get_ftp_folder_no_heartbeat(self):
        survey = json.loads(common_software_survey)
        folder = ftp_helper.get_ftp_folder(survey)
        self.assertEqual(folder, settings.FTP_FOLDER)

    def test_get_ftp_folder_heartbeat_false(self):
        survey = json.loads(common_software_survey)
        survey["heartbeat"] = False
        folder = ftp_helper.get_ftp_folder(survey)
        self.assertEqual(folder, settings.FTP_FOLDER)

    def test_get_ftp_folder_heartbeat_true(self):
        survey = json.loads(common_software_survey)
        survey["heartbeat"] = True
        folder = ftp_helper.get_ftp_folder(survey)
        self.assertEqual(folder, settings.FTP_HEARTBEAT_FOLDER)
