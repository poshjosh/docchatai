import logging.config
import unittest
from datetime import datetime

from docchatai.app.threads import Threads
from test.app.test_functions import get_logging_config

logging.config.dictConfig(get_logging_config())

class BaseTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print(f'{datetime.now().time()} Setting up {cls}')
        Threads.init()

    @classmethod
    def tearDownClass(cls):
        print(f'{datetime.now().time()} Tearing down {cls}')
        Threads.shutdown(wait=True, cancel_futures=False)
