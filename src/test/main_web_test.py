import io
import logging.config
import os.path
import unittest

from docchatai.app.config import ChatVar
from docchatai.main_web import web_app
from test.app.base_test_case import BaseTestCase
from test.app.test_functions import get_logging_config

logging.config.dictConfig(get_logging_config())

class MainWebTestCase(BaseTestCase):
    def setUp(self):
        self.ctx = web_app.app_context()
        self.ctx.push()
        self.client = web_app.test_client()

    def tearDown(self):
        self.ctx.pop()

    def test_home(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    @unittest.skip("Takes too long, because it takes a while to create the chat ai.")
    def test_chat_file_upload(self):
        file = "./test/resources/LITTLE RED RIDING HOOD.pdf"
        response = self.client.post(
            "/chat/file/upload",
            content_type='multipart/form-data',
            data={
                ChatVar.FILE.value: (io.FileIO(file, "rb"), os.path.basename(file))
        })
        print(response.text)
        self.assertEqual(response.status_code, 200)

    @unittest.skip("Takes too long, because chat.invoke() is slow.")
    def test_chat_request(self):
        response = self.client.get("/chat/request", data={
            ChatVar.REQUEST.value: "What is the provided context about?"
        })
        print(response.text)
        self.assertEqual(response.status_code, 200)

if __name__ == "__main__":
    unittest.main()