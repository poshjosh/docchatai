import unittest
from datetime import datetime

from langchain_core.embeddings import FakeEmbeddings
from langchain_core.vectorstores import VectorStore

from docchatai.app.config import ChatConfig
from docchatai.app.vectorstores import VectorStores, VectorStoreLoader, \
    VectorStoreLoaderMultiThreaded, VectorStoreLoaderSync
from test.app.base_test_case import BaseTestCase


class VectorStoresTestCase(BaseTestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.expected_page_count = 3
        self.run_config = ChatConfig()
        self.embeddings = FakeEmbeddings(size=128)

    def test_vectorstore_loader_sync(self):
        print(f'{datetime.now().time()} test_vectorstore_loader_sync')
        vectorstore = self._test_vectorstore_loader(VectorStoreLoaderSync())
        self.assertEqual(self.expected_page_count, VectorStores.len(vectorstore))

    def test_vectorstore_loader_multi_threaded(self):
        print(f'{datetime.now().time()} test_vectorstore_loader_multi_threaded')
        vectorstore = self._test_vectorstore_loader(VectorStoreLoaderMultiThreaded())
        # All the pages have not been fully loaded, by the time we get here.
        self.assertGreater(VectorStores.len(vectorstore), 1)

    def test_vectorstore_loader_get_loaded_pages(self):
        print(f'{datetime.now().time()} test_vectorstore_loader_get_loaded_pages')
        loader = VectorStoreLoaderSync()
        self._test_vectorstore_loader(loader)
        self.assertEqual(loader.get_total_pages(), loader.get_loaded_pages())

    def _test_vectorstore_loader(self, loader: VectorStoreLoader) -> VectorStore:
        vectorstore = loader.load(self.run_config, self.embeddings).wait_till_completed()
        print(f'{datetime.now().time()} DONE loading pages, len: {VectorStores.len(vectorstore)}')
        return vectorstore

if __name__ == '__main__':
    unittest.main()
