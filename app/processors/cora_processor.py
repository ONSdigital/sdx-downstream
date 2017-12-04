from app import settings
from app.processors.processor_base import Processor


class CoraProcessor(Processor):

    def _setup_logger(self):
        """Sets up the logger"""
        if self.survey:
            try:
                metadata = self.survey['metadata']
                self.logger = self.logger.bind(user_id=metadata['user_id'], ru_ref=metadata['ru_ref'])
            except KeyError:
                self.logger.error("Failed to get metadata")

            if 'tx_id' in self.survey:
                self.tx_id = self.survey['tx_id']
                self.logger = self.logger.bind(tx_id=self.tx_id)

    @staticmethod
    def _get_url():
        """Gets the transformer url"""
        sequence_no = Processor._get_sequence_number()
        return "{0}/cora/{1}".format(settings.SDX_TRANSFORM_CORA_URL, sequence_no)
