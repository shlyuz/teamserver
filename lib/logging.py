import sys
import time
import logging

class Logging(object):
    def __init__(self, args):
        """

        :param kwargs:
        """
        self.info = {"name": "logging",
                     "author": "und3rf10w"
                     }
        super(Logging, self).__init__()
        self.debug = args
        # TODO: Support logging to a file
        if self.debug:
            logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.DEBUG)
        else:
            logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)

    def log(self, msg, level="info", source=None):
        """
        Generates a log message given the message and level

        :param msg: The message to put in the log
        :param level: one of 'info', 'verbose', 'debug', 'warning', 'critical' or 'error', default: info
        :param source: literally just use to get the source of a message if given
        :return:
        """

        if level.lower() in ['critical', 'crit']:
            log_level = logging.CRITICAL
        if level.lower() in ['error', 'err']:
            log_level = logging.ERROR
        if level.lower() in ['warn', 'warning']:
            log_level = logging.WARNING
        if level.lower() == 'info':
            log_level = logging.INFO
        if level.lower() == 'debug':
            log_level = logging.DEBUG
        else:
            # Default to INFO
            log_level = logging.INFO

        if source:
            logging.log(log_level, msg=f"{time.strftime('%Y/%m/%d %H:%M:%S', time.gmtime())} [{source.upper()}]: {msg}")
        else:
            logging.log(log_level, msg=f"{time.strftime('%Y/%m/%d %H:%M:%S', time.gmtime())}: {msg}")
