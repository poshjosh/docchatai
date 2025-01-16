import hashlib
import logging
import os.path
import re
from abc import abstractmethod
from concurrent import futures
from typing import Iterator

from langchain.embeddings import CacheBackedEmbeddings
from langchain.storage import LocalFileStore
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import VectorStore
from langchain_text_splitters import TextSplitter, RecursiveCharacterTextSplitter

from .config import RunConfig
from .threads import Threads

logger = logging.getLogger(__name__)


class VectorStores:
    non_alpha_numeric_pattern = re.compile('[^A-Za-z0-9_-]+')

    @staticmethod
    def _unique_name(chat_model_name: str, input_file_path: str) -> str:
        # Keep these to provide a glimpse of the which chat model and file was used.
        chat_model_prefix = VectorStores.non_alpha_numeric_pattern.sub(
            '_', chat_model_name[:32])
        input_file_suffix = VectorStores.non_alpha_numeric_pattern.sub(
            '_', os.path.basename(input_file_path)[-32:])
        # Use a hash to keep the name short and unique.
        hash_hex = hashlib.sha256(f'{chat_model_name}{input_file_path}'.encode()).hexdigest()
        return f'{chat_model_prefix}_{input_file_suffix}_{hash_hex}'

    @staticmethod
    def len(vectorstore) -> int:
        return 0 if vectorstore is None else len(vectorstore.index_to_docstore_id)

    @staticmethod
    def file_backed_embeddings(run_config: RunConfig, embeddings: Embeddings) -> Embeddings:
        store = LocalFileStore(run_config.app_dir + "/.embeddings-cache/")
        namespace = VectorStores._unique_name(run_config.chat_model_name, run_config.input_file)
        return CacheBackedEmbeddings.from_bytes_store(embeddings, store, namespace=namespace)

    @staticmethod
    def yield_pages(input_file_path: str) -> Iterator[Document]:
        loader = PyPDFLoader(input_file_path)
        page_iterator: Iterator[Document] = loader.lazy_load()
        text_splitter: TextSplitter = RecursiveCharacterTextSplitter()

        for page in page_iterator:
            # We pass only one page as an array
            docs = text_splitter.create_documents([page.page_content], [page.metadata])
            if docs is None or len(docs) == 0:
                logger.debug(f'Skipped page: {page.metadata}')
                continue
            logger.debug(f' Parsed page: {page.metadata}')
            yield docs[0]

class VectorStoreLoader:
    @abstractmethod
    def load(self, run_config: RunConfig, embeddings: Embeddings) -> 'VectorStoreLoader':
        raise NotImplementedError()

    @abstractmethod
    def get(self) -> VectorStore:
        raise NotImplementedError()

    @abstractmethod
    def wait_till_completed(self) -> VectorStore:
        raise NotImplementedError()


class VectorStoreLoaderSync(VectorStoreLoader):
    def __init__(self):
        self.__vectorstore = None

    def load(self, run_config: RunConfig, embeddings: Embeddings) -> VectorStoreLoader:
        page_list: [Document] = list(VectorStores.yield_pages(run_config.input_file))
        embeddings = VectorStores.file_backed_embeddings(run_config, embeddings)
        self.__vectorstore = FAISS.from_documents(page_list, embeddings)
        return self

    def get(self) -> VectorStore:
        return self.__vectorstore

    def wait_till_completed(self) -> VectorStore:
        return self.__vectorstore


class VectorStoreLoaderMultiThreaded(VectorStoreLoader):
    def __init__(self, cls=FAISS, batch_size: int = 0):
        self.__cls = cls
        self.__futures = []
        self.__batch_size = batch_size
        self.__vectorstore = None

    def load(self, run_config: RunConfig, embeddings: Embeddings) -> VectorStoreLoader:
        page_list: [Document] = list(VectorStores.yield_pages(run_config.input_file))
        embeddings = VectorStores.file_backed_embeddings(run_config, embeddings)

        if len(page_list) == 0:
            raise ValueError('No valid pages found in the document')

        if self.__batch_size <= 0:
            batch_size = len(page_list) / run_config.max_worker_threads
            if batch_size < 1:
                batch_size = 1
        else:
            batch_size = self.__batch_size

        # First
        first_page = page_list[0]
        if first_page is None:
            raise ValueError('No valid pages found in the document')
        logger.debug(f'Loading page: {first_page.metadata}')
        self.__vectorstore = self.__cls.from_documents([first_page], embeddings)

        # Remaining
        def add_pages_to_store(pages: [Document]):
            try:
                page_nums = ','.join([str(p.metadata['page']) for p in pages])
                logger.debug(f'Loading pages: {page_nums}')
                self.__vectorstore.merge_from(self.__cls.from_documents(pages, embeddings))
            except Exception as ex:
                logger.debug(f'Error loading pages.\n{ex}')

        batch = []
        for page in page_list[1:]:
            batch.append(page)
            if len(batch) >= batch_size:
                self.__futures.append(Threads.submit(add_pages_to_store, batch))
                batch = []
        if len(batch) > 0:
            self.__futures.append(Threads.submit(add_pages_to_store, batch))

        return self

    def get(self) -> VectorStore:
        return self.__vectorstore

    def wait_till_completed(self) -> VectorStore:
        if len(self.__futures) > 0:
            futures.wait(self.__futures)
        return self.__vectorstore
