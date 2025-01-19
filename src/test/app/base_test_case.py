import logging.config
import unittest
from datetime import datetime

from docchatai.app.app import App
from docchatai.app.config import AppConfig
from test.app.test_functions import get_logging_config

logging.config.dictConfig(get_logging_config())

class BaseTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print(f'{datetime.now().time()} Setting up {cls}')
        App.init(AppConfig())

    @classmethod
    def tearDownClass(cls):
        print(f'{datetime.now().time()} Tearing down {cls}')
        App.shutdown(wait=True, cancel_futures=False)
