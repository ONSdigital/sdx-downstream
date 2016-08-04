from app import settings
from app.helpers.request_helper import remote_call, response_ok
from app.processors.survey_processor import SurveyProcessor
from app.queue_publisher import QueuePublisher


class CensusProcessor(SurveyProcessor):

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

        publisher = QueuePublisher(self.logger, settings.RABBIT_URLS, settings.RABBIT_QUEUE_TESTFORM)
        return publisher.publish_message(survey_xml, 'application/xml')
