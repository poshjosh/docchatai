import logging.config
from datetime import datetime

from docchatai.app.app import App
from docchatai.app.config import AppConfig, ChatConfig
from docchatai.app.chat_service import ChatService

app_config = AppConfig()
logging.config.dictConfig(app_config.logging_config)

if __name__ == '__main__':

    try :
        App.init(app_config)

        chat_config = ChatConfig(app_config)

        chat_ai = ChatService().create_chat_ai(chat_config)

        # Start asking questions and getting answers in a loop
        print(f"{datetime.now().time()} Document: {chat_config.chat_file}")
        while True:
            request = input(f'\n{datetime.now().time()} How may I help you?\n')
            result = chat_ai.invoke(request)
            print(f"\n{datetime.now().time()}\n{result}")
    finally:
        App.shutdown()