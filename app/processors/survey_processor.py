class SurveyProcessor(object):

    def __init__(self, logger, survey):
        self.logger = logger
        self.survey = survey
        self.tx_id = None
        self.setup_logger()

    def process(self):
        raise NotImplementedError

    def setup_logger(self):
        if self.survey:
            if 'metadata' in self.survey:
                metadata = self.survey['metadata']
                self.logger = self.logger.bind(user_id=metadata['user_id'], ru_ref=metadata['ru_ref'])

            if 'tx_id' in self.survey:
                self.tx_id = self.survey['tx_id']
                self.logger = self.logger.bind(tx_id=self.tx_id)
