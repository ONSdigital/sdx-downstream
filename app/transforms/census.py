from app import settings
from app.helpers.request_helper import remote_call, response_ok
from app.settings import logger
from app.queue_publisher import QueuePublisher


class Census(object):

    def __init__(self, survey, url):
        self.survey = survey
        self.url = url

    def transform(self):
        response = remote_call(self.url, json=self.survey)
        if not response_ok(response):
            return False

        return response.content

    def process(self):
        survey_xml = self.transform()
        if survey_xml is False:
            return False

        publisher = QueuePublisher(logger, settings.RABBIT_URLS, settings.RABBIT_QUEUE_TESTFORM)
        return publisher.publish_message(survey_xml, 'application/xml')
