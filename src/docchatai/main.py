import logging.config
from datetime import datetime

from app.app import App
from app.config import RunConfig
from docchatai.app.chat_service import ChatService

if __name__ == '__main__':
    run_config = RunConfig()
    logging.config.dictConfig(run_config.logging_config)

    try :
        App.init(run_config)

        chat_ai = ChatService.create_chat_ai(run_config)

        # Start asking questions and getting answers in a loop
        print(f"{datetime.now().time()} Document: {run_config.input_file}")
        while True:
            request = input(f'\n{datetime.now().time()} How may I help you?\n')
            result = chat_ai.invoke(request)
            print(f"\n{datetime.now().time()}\n{result}")
    finally:
        App.shutdown()