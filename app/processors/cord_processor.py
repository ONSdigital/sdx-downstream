from app import settings
from app.processors.processor_base import Processor


class CordProcessor(Processor):

    def __init__(self, survey, ftpconn):
        super().__init__(survey, ftpconn, settings.SDX_TRANSFORM_CS_URL, 'cord')