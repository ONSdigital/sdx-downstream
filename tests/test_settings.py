import os
from app import settings
import unittest


class TestNoBatchTransformService(unittest.TestCase):
    def setUp(self):
        os.environ["SDX_SEQUENCE_URL"] = "SomeUrl"
        os.environ["RABBITMQ_HOST"] = "Host"
        os.environ['RABBITMQ_PORT'] = "Port"
        os.environ['RABBITMQ_DEFAULT_USER'] = "User"
        os.environ['RABBITMQ_DEFAULT_PASS'] = "Password"
        os.environ['RABBITMQ_DEFAULT_VHOST'] = "VHost"

    def test_get_value_returns_environment_value(self):
        sdx_sequence_url = settings._get_value("SDX_SEQUENCE_URL")
        self.assertEqual(sdx_sequence_url, "SomeUrl")

    def test_get_value_returns_default_if_no_environment_variable_found(self):
        val = settings._get_value("SOME_UNKNOWN_ENV", "SomeDefaultValue")
        self.assertEqual(val, "SomeDefaultValue")

    def test_get_value_raises_ValueError_if_no_enviornment_variable_and_no_default(self):
        with self.assertRaises(ValueError):
            settings._get_value("SOME_UNKNOWN_ENV")

    def test_get_raises_ValueError_if_empty_string_set_as_default(self):
        with self.assertRaises(ValueError):
            settings._get_value("SOME_UNKNOWN_ENV", "")
