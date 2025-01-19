import logging
import os
from enum import unique, Enum
from sys import argv

logger = logging.getLogger(__name__)

class AppConfig:
    @property
    def secret_key(self) -> str:
        return os.environ['APP_SECRET_KEY']

    @property
    def app_name(self) -> str:
        return "DocChatAI"

    @property
    def app_title(self) -> str:
        return f"I am {self.app_name}. Ask me anything about any document."

    @property
    def app_dir(self) -> str:
        return os.environ['APP_DIR']

    @property
    def uploads_dir(self) -> str:
        return os.path.join(self.app_dir, 'uploads')

    @property
    def app_port(self) -> int:
        return int(os.environ.get('APP_PORT', '8888'))

    @property
    def is_production(self) -> bool:
        return os.environ.get('APP_PROFILE') == 'prod'

    @property
    def max_results_per_query(self) -> int:
        return int(os.environ.get('MAX_RESULTS_PER_QUERY', '3'))

    @property
    def default_chat_model_provider(self) -> str:
        return 'ollama'

    @property
    def default_chat_model_name(self) -> str:
        return 'llama3.1'

    @property
    def default_chat_message_limit(self) -> int:
        return 100

    @property
    def max_worker_threads(self) -> int:
        return int(os.environ.get('MAX_WORKER_THREADS', '50'))

    @property
    def default_chat_template(self) -> str:
        return """
            You are an information retrieval AI.
            You will provide a relevant response to the request.
            Your response should be based only on the context provided.
            Do not make up any information.
            
            Request: {request}
            
            Context: {context}
        """

    @property
    def logging_config(self):
        log_level = 'INFO' if self.is_production is True else 'DEBUG'
        return {
            'version': 1,
            'formatters': {
                'simple': {'format': '%(asctime)s %(name)s %(levelname)s %(message)s'}},
            'handlers': {'console': {
                'class': 'logging.StreamHandler', 'level': f'{log_level}', 'formatter': 'simple'}},
            'loggers': {
                'docchatai': {'level': f'{log_level}', 'handlers': ['console'], 'propagate': False}}
        }

@unique
class ChatVar(str, Enum):
    def __new__(cls, value):
        obj = str.__new__(cls, [value])
        obj._value_ = value
        return obj
    MODEL_PROVIDER = 'chat_model_provider'
    MODEL = 'chat_model'
    FILE = 'chat_file'
    TEMPLATE = 'chat_template'
    REQUEST = 'chat_request'

class ChatConfig:
    def __init__(self, app_config: AppConfig = AppConfig(), values: dict[str, str] = None):
        super().__init__()
        self.__app_config = app_config
        self.__values = {} if values is None else values

    @property
    def app_config(self) -> AppConfig:
        return self.__app_config

    @property
    def chat_model_provider(self) -> str:
        return self._get_val_key_case_insensitive(
            ChatVar.MODEL_PROVIDER, argv[1] if len(argv) > 1 else self.app_config.default_chat_model_name)

    @property
    def chat_model_name(self) -> str:
        return self._get_val_key_case_insensitive(
            ChatVar.MODEL, argv[2] if len(argv) > 2 else self.app_config.default_chat_model_name)

    @property
    def chat_file(self) -> str:
        return self._get_val_key_case_insensitive(ChatVar.FILE, argv[3] if len(argv) > 3 else None)

    @property
    def chat_template(self) -> str:
        return self._get_val_key_case_insensitive(ChatVar.TEMPLATE, self.app_config.default_chat_template)

    @property
    def chat_request(self) -> str:
        return self._get_val_key_case_insensitive(ChatVar.REQUEST, None)

    def _get_val_key_case_insensitive(self, key: ChatVar, default: str or None) -> str or None:
        key = key.value
        value = self.__values.get(key, os.environ.get(key, None))
        if value is None:
            key = key.upper()
            value = self.__values.get(key, os.environ.get(key, None))
        return default if value is None else value

    def __str__(self):
        return (f'RunConfig: model={self.chat_model_name}, '
                f'max_result_per_query={self.app_config.max_results_per_query}, '
                f'chat_file={self.chat_file}, chat_request={self.chat_request}')