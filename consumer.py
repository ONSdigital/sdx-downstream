import pika
import os
import logging
import sys
import settings
import requests

logging.basicConfig(stream=sys.stdout, level=settings.LOGGING_LEVEL, format=settings.LOGGING_FORMAT)

logging.debug("Starting survey-notification consumer..")

def get_survey_from_store(mongoid):
    store_url = settings.SDX_STORE_URL + "/responses/" + mongoid
    result = requests.get(store_url).text
    logging.debug(result)

def on_message(channel, method_frame, header_frame, body):
    logging.debug( method_frame.delivery_tag )
    get_survey_from_store(body.decode("utf-8"))
    channel.basic_ack(delivery_tag=method_frame.delivery_tag)

connection = pika.BlockingConnection(pika.URLParameters(settings.RABBIT_URL))
channel = connection.channel()
channel.basic_consume(on_message, settings.RABBIT_QUEUE)
try:
    channel.start_consuming()
except KeyboardInterrupt:
    channel.stop_consuming()
connection.close()
