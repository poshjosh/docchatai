import logging
from abc import abstractmethod
from concurrent import futures

from langchain.embeddings import CacheBackedEmbeddings
from langchain.storage import LocalFileStore
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import VectorStore

from .config import ChatConfig
from .concurrency import Threads
from .doc_loader import DocLoader
from .utils import safe_unique_key

logger = logging.getLogger(__name__)


class VectorStores:
    @staticmethod
    def len(vectorstore) -> int:
        return 0 if vectorstore is None else len(vectorstore.index_to_docstore_id)

    @staticmethod
    def file_backed_embeddings(chat_config: ChatConfig, embeddings: Embeddings) -> Embeddings:
        store = LocalFileStore(chat_config.app_config.app_dir + "/.embeddings-cache/")
        namespace = safe_unique_key(chat_config.chat_file, chat_config.chat_model_name)
        return CacheBackedEmbeddings.from_bytes_store(embeddings, store, namespace=namespace)

class VectorStoreLoader:
    @abstractmethod
    def load(self, run_config: ChatConfig, embeddings: Embeddings) -> 'VectorStoreLoader':
        raise NotImplementedError()

    @abstractmethod
    def get_loaded_pages(self) -> int:
        raise NotImplementedError()

    @abstractmethod
    def get_total_pages(self) -> int:
        raise NotImplementedError()

    @abstractmethod
    def get(self) -> VectorStore:
        raise NotImplementedError()

    @abstractmethod
    def wait_till_completed(self) -> VectorStore:
        raise NotImplementedError()


class VectorStoreLoaderSync(VectorStoreLoader):
    def __init__(self, cls=FAISS):
        self.__cls = cls
        self.__total_pages = None
        self.__vectorstore: VectorStore or None = None

    def load(self, chat_config: ChatConfig, embeddings: Embeddings) -> VectorStoreLoader:
        page_list: [Document] = list(DocLoader.yield_pages(chat_config.chat_file))
        self.__total_pages = len(page_list)
        embeddings = VectorStores.file_backed_embeddings(chat_config, embeddings)
        self.__vectorstore = self.__cls.from_documents(page_list, embeddings)
        return self

    def get_loaded_pages(self) -> int:
        if self.__vectorstore is None:
            raise ValueError('First call load(), before querying loaded pages')
        return VectorStores.len(self.__vectorstore)

    def get_total_pages(self) -> int:
        if self.__total_pages is None:
            raise ValueError('First call load(), before querying total pages')
        return self.__total_pages

    def get(self) -> VectorStore:
        return self.__vectorstore

    def wait_till_completed(self) -> VectorStore:
        return self.__vectorstore


class VectorStoreLoaderMultiThreaded(VectorStoreLoader):
    def __init__(self, cls=FAISS):
        self.__cls = cls
        self.__total_pages = None
        self.__futures = []
        self.__vectorstore: VectorStores or None = None

    def load(self, chat_config: ChatConfig, embeddings: Embeddings) -> VectorStoreLoader:
        page_list: [Document] = list(DocLoader.yield_pages(chat_config.chat_file))
        self.__total_pages = len(page_list)
        embeddings = VectorStores.file_backed_embeddings(chat_config, embeddings)

        if self.__total_pages == 0:
            raise ValueError('No valid pages found in the document')

        batch_size = self.__total_pages / chat_config.app_config.max_worker_threads
        if batch_size < 1:
            batch_size = 1

        # First
        first_page = page_list[0]
        if first_page is None:
            raise ValueError('No valid pages found in the document')
        self.__vectorstore = self.__cls.from_documents([first_page], embeddings)
        logger.debug('Saved first page')

        # Remaining
        def add_pages_to_store(pages: [Document]):
            page_nums = None
            try:
                if len(pages) == 0:
                    return

                vectorstore = self.__cls.from_documents(pages, embeddings)
                self.__vectorstore.merge_from(vectorstore)

                page_nums = ','.join([str(p.metadata['page']) for p in pages])
                logger.debug(f'Saved pages: {page_nums}')

            except Exception as ex:
                logger.error('Error loading pages: %s. %s', page_nums, ex, exc_info=True)

        batch = []
        for page in page_list[1:]:
            batch.append(page)
            if len(batch) >= batch_size:
                self.__futures.append(Threads.submit(add_pages_to_store, batch))
                batch = []

        if len(batch) > 0:
            self.__futures.append(Threads.submit(add_pages_to_store, batch))

        return self

    def get_loaded_pages(self) -> int:
        if self.__vectorstore is None:
            raise ValueError('First call load(), before querying loaded pages')
        return VectorStores.len(self.__vectorstore)

    def get_total_pages(self) -> int:
        if self.__total_pages is None:
            raise ValueError('First call load(), before querying total pages')
        return self.__total_pages

    def get(self) -> VectorStore:
        return self.__vectorstore

    def wait_till_completed(self) -> VectorStore:
        if len(self.__futures) > 0:
            futures.wait(self.__futures)
        return self.__vectorstore
