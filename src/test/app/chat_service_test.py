import unittest
from datetime import datetime

from docchatai.app.chat_service import ChatService
from docchatai.app.config import ChatConfig
from docchatai.app.vectorstores import VectorStoreLoader, \
    VectorStoreLoaderMultiThreaded, VectorStoreLoaderSync
from test.app.base_test_case import BaseTestCase

class TestChatConfig(ChatConfig):
    @property
    def max_worker_threads(self) -> int:
        return 3

    @property
    def chat_file(self) -> str:
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
        self.run_config = TestChatConfig()

    def test_create_chat_ai_sync(self):
        print(f'{datetime.now().time()} test_create_chat_ai_sync')
        self._test_create_chat_ai(VectorStoreLoaderSync())

    def test_create_chat_ai_multi_threaded(self):
        print(f'{datetime.now().time()} test_create_chat_ai_multi_threaded')
        self._test_create_chat_ai(VectorStoreLoaderMultiThreaded())

    def _test_create_chat_ai(self, vectorstore_loader: VectorStoreLoader):

        class TestChatService(ChatService):
            def new_vectorstore_loader(self) -> VectorStoreLoader:
                return vectorstore_loader

        chat_ai = TestChatService().create_chat_ai(self.run_config)
        self.assertIsNotNone(chat_ai)
        func_invoke = getattr(chat_ai, "invoke", None)
        if not callable(func_invoke):
            self.fail("The created Chat AI does not have an invoke method.")
        # request = "What is the provided context about?"
        # print(f'{datetime.now().time()} Request: {request}')
        # response = chat_ai.invoke(request)
        # print(f'{datetime.now().time()} Response: {response}')
        # self.assertIsNotNone(response)

if __name__ == '__main__':
    unittest.main()
