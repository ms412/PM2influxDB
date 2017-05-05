import logging


class logger(object):

    def __init__(self,config):

        self._filename = config.get('LOGFILE','logger.log')
        self._level = config.get('LOGLEVEL','INFO')
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(self._level)

        handler = logging.FileHandler(self._filename)
       # handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(module)s - %(funcName)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self._logger.addHandler(handler)

    def start(self):
     #   self._logger.info('Start Logging')
        return self._logger
