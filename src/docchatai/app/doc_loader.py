import logging
from typing import Iterator

from langchain_community.document_loaders import PyPDFLoader, CSVLoader, Docx2txtLoader, TextLoader
from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document
from langchain_text_splitters import TextSplitter, RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)


class UnsupportedFileTypeError(Exception):
    def __init__(self, *args):
        super().__init__(*args)
        self.message = args[0]


class DocLoader:
    @staticmethod
    def get_supported_file_extensions() -> [str]:
        return ['.txt', '.csv', '.docx', '.pdf']

    @staticmethod
    def yield_pages(input_file_path: str) -> Iterator[Document]:
        loader = DocLoader.get_loader(input_file_path)
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

    @staticmethod
    def get_loader(input_file_path: str) -> BaseLoader:
        input_file_path = input_file_path.lower()
        if input_file_path.endswith('.txt'):
            return TextLoader(input_file_path)
        if input_file_path.endswith('.csv'):
            return CSVLoader(input_file_path)
        if input_file_path.endswith('.docx'):
            return Docx2txtLoader(input_file_path)
        if input_file_path.endswith('.pdf'):
            return PyPDFLoader(input_file_path)
        raise UnsupportedFileTypeError(f'Unsupported file type: `{input_file_path}`. '
                                       f'Supported: {DocLoader.get_supported_file_extensions()}')
