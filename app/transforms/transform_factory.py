from app import settings
from app.transforms.census import Census
from app.transforms.common_software import CommonSoftware


class TransformFactory(object):

    @staticmethod
    def get_transform(survey):
        s_id = survey['survey_id']
        s_instrument_id = survey['collection']['instrument_id']
        identifier = "{0}.{1}".format(s_id, s_instrument_id)

        if identifier == settings.CENSUS_CE_IDENTIFIER:
            settings.logger.debug("Census CE Transform", identifier=identifier)
            url = "{0}/cexml".format(settings.SDX_TRANSFORM_TESTFORM_URL)
            return Census(survey, url)

        if identifier == settings.CENSUS_HH_IDENTIFIER:
            settings.logger.debug("Census HH Transform", identifier=identifier)
            url = "{0}/hhxml".format(settings.SDX_TRANSFORM_TESTFORM_URL)
            return Census(survey, url)

        # default
        settings.logger.debug("Common Software Transform", identifier=identifier)
        return CommonSoftware(survey)
