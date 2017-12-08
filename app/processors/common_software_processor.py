from app import settings
from app.processors.processor_base import Processor


class CommonSoftwareProcessor(Processor):

    def __init__(self, logger, survey, ftpconn):
        super().__init__(logger, survey, ftpconn, settings.SDX_TRANSFORM_CS_URL, 'common-software')
