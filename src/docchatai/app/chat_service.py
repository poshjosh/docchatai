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

    def __init__(self, message_display_limit: int = 100):
        self.__message_display_limit = message_display_limit

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

    def chat_request(self, session_id: str, request: str, chat_config: ChatConfig) -> [dict[str, any]]:
        chat_ai = self.get_chat_ai(session_id)
        if chat_ai is None:
            chat_ai = self.add_chat_ai(session_id, chat_config)

        response = chat_ai.invoke(request)
        logger.debug("Chat response ready")

        session_store = ChatService._get_session_store(session_id)
        chats = session_store.get('chats', None)
        if chats is None:
            chats = []
            session_store['chats'] = chats

        chats.append({'request': request, 'response': response})
        logger.debug('Session chats: %s', len(chats))

        return chats[-self.__message_display_limit:]

class EchoChatService(ChatService):
    def create_chat_ai(self, chat_config: ChatConfig, _: bool = True):
        class EchoChat:
            def __init__(self, sleep_time: int = 3):
                self.__sleep_time = sleep_time

            def invoke(self, request: str) -> str:
                time.sleep(self.__sleep_time)
                return request

        return EchoChat()

# class ChatModel:
#     def __init__(self, name: str, provider: str or None = None):
#         self.name = name
#         self.provider = provider
#
#     def to_dict(self):
#         return {'name': self.name, 'provider': self.provider}
#
#     def __str__(self):
#         return f'ChatModel({str(self.to_dict())})'
#
# class Chat:
#     def __init__(self, request: str, response: str or None = None):
#         self.request = request
#         self.response = response
#
#     def to_dict(self):
#         return {'request': self.request, 'response': self.response}
#
#     def __str__(self):
#         return f'Chat({str(self.to_dict())})'
#
# class ChatSession:
#     @staticmethod
#     def from_config(chat_config: ChatConfig) -> 'ChatSession':
#         chat_session = ChatSession()
#         chat_session.model = ChatModel(chat_config.chat_model_name, chat_config.chat_model_provider)
#         chat_session.template = chat_config.chat_template
#         chat_session.file_path = chat_config.chat_file
#         return chat_session
#
#     @staticmethod
#     def from_dict(data: dict[str, any]) -> 'ChatSession':
#         chat_session = ChatSession()
#         chat_session.model = ChatModel(data['model']['name'], data['model']['provider'])
#         chat_session.template = data['template']
#         chat_session.last_request = data['last_request']
#         chat_session.chats = [Chat(chat['request'], chat['response']) for chat in data['messages']]
#         chat_session.original_file_name = data['original_file_name']
#         chat_session.file_path = data['file_path']
#         return chat_session
#
#     def __init__(self):
#         self.model: ChatModel or None = None
#         self.template: str or None = None
#         self.last_request: str or None = None
#         self.chats: List[Chat] or None = None
#         self.original_file_name: str or None = None
#         self.file_path: str or None = None
#
#     def to_dict(self):
#         return {
#             'model': self.model.to_dict() if self.model is not None else None,
#             'template': self.template,
#             'last_request': self.last_request,
#             'chats': [chat.to_dict() for chat in self.chats] if self.chats is not None else None,
#             'original_file_name': self.original_file_name,
#             'file_path': self.file_path
#         }
#
#     def __str__(self):
#         return f'ChatSession({str(self.to_dict())})'
