import pika
from app import settings
from app.helpers.request_helper import remote_call, response_ok
from app.settings import logger


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
        content = self.transform()
        if content is False:
            return False

        try:
            logger.debug("XML Queueing Start")
            connection = pika.BlockingConnection(pika.URLParameters(settings.RABBIT_URL))
            channel = connection.channel()
            channel.queue_declare(queue=settings.RABBIT_QUEUE_TESTFORM)
            channel.basic_publish(exchange='',
                                  properties=pika.BasicProperties(content_type='application/xml'),
                                  routing_key=settings.RABBIT_QUEUE_TESTFORM,
                                  body=content)
            logger.debug("XML Queuing Success")
            connection.close()
            return True

        except:
            logger.error("XML Queuing Failed")
            return False
