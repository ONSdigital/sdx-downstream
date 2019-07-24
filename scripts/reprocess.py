import sys
import os
parent_dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(parent_dir_path)

from sdc.rabbit import QueuePublisher
from sdc.rabbit.exceptions import PublishMessageError

from app import settings

publisher = QueuePublisher(settings.RABBIT_URLS,
                           'sdx-survey-notification-durable')

if __name__ == "__main__":
    with open('tx_ids', 'r') as fp:
        lines = list(fp)

    if not lines:
        sys.exit("No tx_ids in file, exiting script")

    for tx_id in lines:
        # Remove newline character at the end of the tx_id (if present)
        tx_id = tx_id.rstrip()
        print(f"About to put {tx_id} on the queue")
        try:
            publisher.publish_message(tx_id, headers={'tx_id': tx_id})
        except PublishMessageError as e:
            print(e)
            raise
