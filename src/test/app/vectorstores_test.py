import logging.config
import time
import unittest
from datetime import datetime

from langchain_core.embeddings import FakeEmbeddings

from docchatai.app.config import RunConfig
from docchatai.app.threads import Threads
from docchatai.app.vectorstores import VectorStoreLoader, VectorStores
from test.app.test_functions import get_logging_config

logging.config.dictConfig(get_logging_config())

class VectorStoresTestCase(unittest.TestCase):
    @classmethod
    def tearDownClass(cls):
        print(f'{datetime.now().time()} Tearing down {cls}')
        Threads.shutdown(wait=True, cancel_futures=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.run_config = RunConfig()
        self.embeddings = FakeEmbeddings(size=128)

    def test_faiss_vectorstore(self):
        print(f'{datetime.now().time()} test_faiss_vectorstore')
        self.assertEqual(3, VectorStores.len(VectorStores.faiss(self.run_config, self.embeddings)))

    # @unittest.skip("Lasts too long. Had to sleep for 5 seconds to allow the store to fully load")
    def test_vectorstore_loader(self):
        print(f'{datetime.now().time()} test_vectorstore_loader')
        uut = VectorStoreLoader()
        vectorstore = uut.load(self.run_config, self.embeddings)
        uut.wait_till_completed()
        time.sleep(5) # Give some time for the store to fully load
        self.assertEqual(3, VectorStores.len(vectorstore))


if __name__ == '__main__':
    unittest.main()
