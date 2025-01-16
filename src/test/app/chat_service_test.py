import unittest
from datetime import datetime

from docchatai.app.chat_service import ChatService
from docchatai.app.config import RunConfig
from docchatai.app.vectorstores import VectorStoreLoader, \
    VectorStoreLoaderMultiThreaded, VectorStoreLoaderSync
from test.app.base_test_case import BaseTestCase

class TestRunConfig(RunConfig):
    @property
    def input_file(self) -> str:
        return "./test/resources/CODE REVIEW BEST PRACTICES.pdf"

    @property
    def default_chat_template(self) -> str:
        return """
            You are an information retrieval AI.
            You will provide a relevant response to the request.
            Your response should be based only on the provided context.
            Do not make up any information.
            
            Request: {request}
            
            Context: {context}
        """


class ChatServiceTestCase(BaseTestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.run_config = TestRunConfig()

    def test_create_chat_ai_sync(self):
        print(f'{datetime.now().time()} test_create_chat_ai_sync')
        self._test_create_chat_ai(VectorStoreLoaderSync())

    def test_create_chat_ai_multi_threaded(self):
        print(f'{datetime.now().time()} test_create_chat_ai_multi_threaded')
        self._test_create_chat_ai(VectorStoreLoaderMultiThreaded())

    def _test_create_chat_ai(self, vectorstore_loader: VectorStoreLoader):
        chat_ai = ChatService(vectorstore_loader).create_chat_ai(self.run_config)
        request = "What is the provided context about?"
        print(f'{datetime.now().time()} Request: {request}')
        response = chat_ai.invoke(request)
        print(f'{datetime.now().time()} Response: {response}')
        self.assertIsNotNone(response)

if __name__ == '__main__':
    unittest.main()
