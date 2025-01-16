import logging

import time

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

from .config import RunConfig
from .vectorstores import VectorStoreLoader, VectorStoreLoaderMultiThreaded

logger = logging.getLogger(__name__)

class ChatService:
    __store = {}
    def __init__(self, vectorstore_loader: VectorStoreLoader = VectorStoreLoaderMultiThreaded()):
        self.__vectorstore_loader = vectorstore_loader

    @staticmethod
    def model(name: str, provider: str):
        from langchain.chat_models import init_chat_model
        return init_chat_model(name, model_provider=provider, temperature=0)

    @staticmethod
    def embeddings(name: str, provider: str):
        if provider == 'ollama':
            from langchain_ollama.embeddings import OllamaEmbeddings
            return OllamaEmbeddings(model=name)
        # TODO - Add embeddings for more providers.
        else:
            raise ValueError(f'Unsupported model provider for embeddings: {provider}')

    def create_chat_ai(self, run_config: RunConfig, wait_till_completed: bool = True):
        logger.debug('create_chat_ai')
        chat_prompt = ChatPromptTemplate.from_template(run_config.chat_template)

        chat_model = ChatService.model(run_config.chat_model_name, run_config.chat_model_provider)
        embeddings = ChatService.embeddings(run_config.chat_model_name, run_config.chat_model_provider)
        logger.debug(f'Chat model ready: {run_config.chat_model_name}')

        loader = self.__vectorstore_loader.load(run_config, embeddings)
        vectorstore = loader.wait_till_completed() if wait_till_completed is True else loader.get()
        logger.debug(f'Vectorstore ready: {vectorstore}')

        retriever = vectorstore.as_retriever(search_kwargs={'k': run_config.max_results_per_query})

        return (
                {
                    'request': RunnablePassthrough(),
                    'context': retriever,
                }
                | chat_prompt
                | chat_model
                | StrOutputParser()
        )

    def chat_request(self,
                     session_id: str,
                     request_data: dict[str, any],
                     limit: int = 100) -> [dict[str, any]]:
        logger.debug('chat_request, request_data: %s', request_data)

        store = ChatService.__store.get(session_id, None)
        if store is None:
            store = {}
            ChatService.__store[session_id] = store

        chat_ai = store.get('chat_ai', None)
        if chat_ai is None:
            run_config = RunConfig()
            chat_ai = self.create_chat_ai(run_config)
            store['chat_ai'] = chat_ai

        request = request_data['request']
        logger.debug("Chat request: %s", request)
        response = chat_ai.invoke(request)
        logger.debug("Chat response: %s", response)

        chats = store.get('chats', None)
        if chats is None:
            chats = []
            store['chats'] = chats

        chats.append({'request': request, 'response': response})
        logger.debug('Session chats: %s', chats)

        return chats[-limit:]

class EchoChatService(ChatService):
    def create_chat_ai(self, run_config: RunConfig, _: bool = True):
        class EchoChat:
            def __init__(self, sleep_time: int = 3):
                self.__sleep_time = sleep_time

            def invoke(self, request: str) -> str:
                time.sleep(self.__sleep_time)
                return request

        return EchoChat()
