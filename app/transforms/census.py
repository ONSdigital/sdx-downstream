from app import settings
from app.settings import logger
from app.helpers.request_helper import remote_call, response_ok
from app.queue_publisher import QueuePublisher


class Census(object):

    def __init__(self, survey):
        self.survey = survey

    def get_url(self):
        return "{0}/census".format(settings.SDX_TRANSFORM_TESTFORM_URL)

    def transform(self):
        response = remote_call(self.get_url(), json=self.survey)
        if not response_ok(response):
            return False

        return response.content

    def process(self):
        survey_xml = self.transform()
        if survey_xml is False:
            return False

        publisher = QueuePublisher(logger, settings.RABBIT_URLS, settings.RABBIT_QUEUE_TESTFORM)
        return publisher.publish_message(survey_xml, 'application/xml')
