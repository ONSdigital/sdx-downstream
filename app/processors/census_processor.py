from app import settings
from app.helpers.request_helper import remote_call, response_ok
from app.processors.survey_processor import SurveyProcessor
from app.queue_publisher import QueuePublisher


class CensusProcessor(SurveyProcessor):

    def get_url(self):
        return "{0}/xml".format(settings.SDX_TRANSFORM_TESTFORM_URL)

    def transform(self):
        response = remote_call(self.get_url(), json=self.survey)
        if not response_ok(response):
            return None

        return response.content

    def deliver_xml(self, survey_xml):
        publisher = QueuePublisher(self.logger, settings.RABBIT_URLS, settings.RABBIT_QUEUE_TESTFORM)
        return publisher.publish_message(survey_xml, 'application/xml')

    def process(self):
        survey_xml = self.transform()
        if survey_xml is None:
            return False

        return self.deliver_xml(survey_xml)
