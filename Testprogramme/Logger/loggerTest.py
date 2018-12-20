#!/usr/bin/env python3
# This Python file uses the following encoding: utf-8
# Name:       loggerTest.py
# Kommentar:  Testprogramm zum Verhalten eines Loggers.
#             Logging Ausgaben in Konsole und Datei
#             Begrenzung der max. Dateigöße
#             https://docs.python.org/3/howto/logging-cookbook.html
#             https://stackoverflow.com/questions/24505145/how-to-limit-log-file-size-in-python
# Autor:      Jan Stietenroth, Okt, 2017
# Version:    0.1

import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger('simple_example')
logger.setLevel(logging.DEBUG)

# create console handler which logs even debug messages
logFormatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(logFormatter)
ch.setLevel(logging.DEBUG)

# create file handler with a higher log level and a rotating file (max. size)
logFile = "./Log.txt"
logfileFormatter = logging.Formatter('%(asctime)s %(levelname)s - %(filename)s(%(lineno)d) %(funcName)s: %(message)s')
fh = RotatingFileHandler(logFile, mode='a', maxBytes=1*1*1024, backupCount=1, encoding=None, delay=0)
fh.setFormatter(logfileFormatter)
fh.setLevel(logging.INFO)

# add the handlers to logger
logger.addHandler(ch)
logger.addHandler(fh)

# 'application' code
logger.debug('debug message')
logger.info('info message')
logger.warn('warn message')
logger.error('error message')
logger.critical('critical message')

##############
import time
while(True):
	logger.info(time.ctime())
	time.sleep(1)
#logger.shutdown() ->Wird nie erreicht, sollte aber getan werden.
