import logging

import time
from langchain_core.language_models import BaseChatModel

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

from .config import ChatConfig
from .vectorstores import VectorStoreLoader, VectorStoreLoaderMultiThreaded

logger = logging.getLogger(__name__)

class ChatAI:
    def __init__(self,
                 loader: VectorStoreLoader,
                 model: BaseChatModel,
                 prompt: ChatPromptTemplate,
                 search_kwargs: dict[str, any]):
        self.__loader: VectorStoreLoader = loader
        self.__model: BaseChatModel = model
        self.__prompt: ChatPromptTemplate = prompt
        self.__search_kwargs = search_kwargs

    def invoke(self, request: str) -> str:
        return self.get_handler().invoke(request)

    def get_handler(self):
        return (
                {
                    'request': RunnablePassthrough(),
                    'context': self.__loader.get().as_retriever(search_kwargs=self.__search_kwargs),
                }
                | self.__prompt
                | self.__model
                | StrOutputParser()
        )

    def get_loader(self) -> VectorStoreLoader:
        return self.__loader

    def get_model(self) -> BaseChatModel:
        return self.__model

    def get_prompt(self) -> ChatPromptTemplate:
        return self.__prompt

    def get_search_kwargs(self) -> dict[str, any]:
        return self.__search_kwargs

class ChatService:
    __store = {}

    @staticmethod
    def get_chat_models() -> [dict[str, str]]:
        return [
            {'name': 'llama3.1', 'provider': 'ollama'},
        ]

    @staticmethod
    def model(name: str, provider: str):
        from langchain.chat_models import init_chat_model
        return init_chat_model(name, model_provider=provider, temperature=1.0)

    @staticmethod
    def embeddings(name: str, provider: str):
        if provider == 'ollama':
            from langchain_ollama.embeddings import OllamaEmbeddings
            return OllamaEmbeddings(model=name)
        # TODO - Add embeddings for more providers.
        else:
            raise ValueError(f'Unsupported model provider for embeddings: {provider}')

    def new_vectorstore_loader(self) -> VectorStoreLoader:
        return VectorStoreLoaderMultiThreaded()

    def create_chat_ai(self, chat_config: ChatConfig, wait_till_completed: bool = True) -> ChatAI:
        logger.debug('chat_config: %s', chat_config)
        chat_prompt = ChatPromptTemplate.from_template(chat_config.chat_template)

        chat_model = ChatService.model(chat_config.chat_model_name, chat_config.chat_model_provider)
        embeddings = ChatService.embeddings(chat_config.chat_model_name, chat_config.chat_model_provider)
        logger.debug(f'Chat model ready: {chat_config.chat_model_name}')

        loader = self.new_vectorstore_loader().load(chat_config, embeddings)
        vectorstore = loader.wait_till_completed() if wait_till_completed is True else loader.get()
        logger.debug(f'Vectorstore ready: {vectorstore}')

        return ChatAI(loader, chat_model, chat_prompt,
                      {'k': chat_config.app_config.max_results_per_query})

    @staticmethod
    def _get_session_store(session_id: str):
        session_store = ChatService.__store.get(session_id, None)
        if session_store is None:
            session_store = {}
            ChatService.__store[session_id] = session_store
        return session_store

    def add_chat_ai(self,
                    session_id: str,
                    chat_config: ChatConfig,
                    wait_till_completed: bool = True) -> ChatAI:
        session_store = ChatService._get_session_store(session_id)
        chat_ai = self.create_chat_ai(chat_config, wait_till_completed)
        session_store['chat_ai'] = chat_ai
        return chat_ai

    @staticmethod
    def get_chat_ai(session_id: str) -> ChatAI or None:
        session_store = ChatService._get_session_store(session_id)
        return session_store.get('chat_ai', None)

    def chat_request(self,
                     session_id: str,
                     chat_config: ChatConfig,
                     limit: int = 100) -> [dict[str, any]]:
        chat_ai = self.get_chat_ai(session_id)
        if chat_ai is None:
            chat_ai = self.add_chat_ai(session_id, chat_config)

        response = chat_ai.invoke(chat_config.chat_request)
        logger.debug("Chat response ready")

        session_store = ChatService._get_session_store(session_id)
        chats = session_store.get('chats', None)
        if chats is None:
            chats = []
            session_store['chats'] = chats

        chats.append({'request': chat_config.chat_request, 'response': response})
        logger.debug('Session chats: %s', len(chats))

        return chats[-limit:]


class EchoChatService(ChatService):
    def create_chat_ai(self, chat_config: ChatConfig, _: bool = True):
        class EchoChat:
            def __init__(self, sleep_time: int = 3):
                self.__sleep_time = sleep_time

            def invoke(self, request: str) -> str:
                time.sleep(self.__sleep_time)
                return request

        return EchoChat()
