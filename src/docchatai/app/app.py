import logging
import signal
import sys
from datetime import datetime

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

from .chat_models import ChatModels
from .config import RunConfig
from .threads import Threads
from .vectorstores import VectorStoreLoader

logger = logging.getLogger(__name__)

class App:
    __shutting_down = False
    __shutdown = False

    @staticmethod
    def shutdown(wait: bool = False, cancel_futures: bool = True):
        if App.__shutting_down is True:
            msg = "Already shutting down..." if App.__shutdown is False else "Already shut down"
            logger.info(msg)
            return
        App.__shutting_down = True
        logger.info("Shutting down...")
        Threads.shutdown(wait=wait, cancel_futures=cancel_futures)
        App.__shutdown = True

    @staticmethod
    def is_shutdown() -> bool:
        return App.__shutdown

    @staticmethod
    def is_shutting_down() -> bool:
        return App.__shutting_down

    @staticmethod
    def run(run_config: RunConfig):
        logger.debug(f'run {run_config}')

        chat_prompt = ChatPromptTemplate.from_template(run_config.chat_template)

        chat_model = ChatModels.model(run_config.chat_model_name, run_config.chat_model_provider)
        embeddings = ChatModels.embeddings(run_config.chat_model_name, run_config.chat_model_provider)
        logger.debug(f'Chat model ready: {run_config.chat_model_name}')

        loader = VectorStoreLoader()
        vectorstore = loader.load(run_config, embeddings)
        loader.wait_till_completed()

        retriever = vectorstore.as_retriever(search_kwargs={'k': run_config.max_results_per_query})

        runnable = (
                {
                    'request': RunnablePassthrough(),
                    'context': retriever,
                }
                | chat_prompt
                | chat_model
                | StrOutputParser()
        )

        # Start asking questions and getting answers in a loop
        print(f"{datetime.now().time()} Document: {run_config.input_file}")
        while True:
            request = input(f'\n{datetime.now().time()} How may I help you?\n')
            result = runnable.invoke(request)
            print(f"\n{datetime.now().time()}\n{result}")


def _terminate_app(signum, _):
    try:
        print(f"{datetime.now().time()} Received signal {signum}")
        App.shutdown()
    finally:
        # TODO - Find out why shutdown is not achieved without this. On the other hand,
        #  when we remove this, we OFTEN receive the following warning:
        #  UserWarning: resource_tracker: There appear to be 2 leaked semaphore objects to clean up at shutdown
        print(f"{datetime.now().time()} Exiting")
        sys.exit(1)

signal.signal(signal.SIGINT, _terminate_app)
signal.signal(signal.SIGTERM, _terminate_app)

