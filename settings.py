import logging
import os

logger = logging.getLogger(__name__)

LOGGING_FORMAT = "%(asctime)s|%(levelname)s: %(message)s"
LOGGING_LOCATION = "logs/downstream.log"
LOGGING_LEVEL = logging.DEBUG

# Default to true, cast to boolean
SDX_STORE_URL = os.getenv("SDX_STORE_URL", "http://localhost:8080")
SDX_TRANSFORM_CS_URL = os.getenv("SDX_TRANSFORM_CS_URL", "http://localhost:5001")
