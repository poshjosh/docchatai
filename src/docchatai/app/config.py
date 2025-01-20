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
    def __new__(cls, value, sys_arg_index: int = -1):
        obj = str.__new__(cls, [value])
        obj._value_ = value
        obj.__sys_arg_index = sys_arg_index
        return obj

    @property
    def sys_arg_index(self) -> int:
        return self.__sys_arg_index

    MODEL_PROVIDER = ('chat_model_provider', 1)
    MODEL = ('chat_model', 2)
    FILE = ('chat_file', 3)
    TEMPLATE = 'chat_template'
    REQUEST = 'chat_request'

class ChatConfig:
    @staticmethod
    def from_sys_args(app_config: AppConfig = AppConfig()) -> 'ChatConfig':
        args = {}
        for e in ChatVar:
            en = ChatVar(e)
            if 0 < en.sys_arg_index < len(argv):
                args[str(en.value)] = argv[en.sys_arg_index]
        return ChatConfig(app_config, args)

    @staticmethod
    def from_dict(app_config: AppConfig = AppConfig(), values: dict[str, str] = None) -> 'ChatConfig':
        return ChatConfig(app_config, values)

    def __init__(self, app_config: AppConfig = AppConfig(), values: dict[str, str] = None):
        super().__init__()
        self.__app_config = app_config
        self.__values = {} if values is None else values

    def to_dict(self) -> dict[str, str]:
        return {
            str(ChatVar.MODEL_PROVIDER.value): self.chat_model_provider,
            str(ChatVar.MODEL.value): self.chat_model_name,
            str(ChatVar.FILE.value): self.chat_file,
            str(ChatVar.TEMPLATE.value): self.chat_template
        }

    @property
    def app_config(self) -> AppConfig:
        return self.__app_config

    @property
    def chat_model_provider(self) -> str:
        return self._get_val_key_case_insensitive(
            ChatVar.MODEL_PROVIDER, self.app_config.default_chat_model_name)

    @property
    def chat_model_name(self) -> str:
        return self._get_val_key_case_insensitive(ChatVar.MODEL, self.app_config.default_chat_model_name)

    @property
    def chat_file(self) -> str:
        return self._get_val_key_case_insensitive(ChatVar.FILE, None)

    @property
    def chat_template(self) -> str:
        return self._get_val_key_case_insensitive(ChatVar.TEMPLATE, self.app_config.default_chat_template)

    def _get_val_key_case_insensitive(self, key: ChatVar, default: str or None) -> str or None:
        key = str(key.value)
        value = self.__values.get(key, os.environ.get(key, None))
        if value is None:
            key = key.upper()
            value = self.__values.get(key, os.environ.get(key, None))
        return default if value is None else value

    def __str__(self):
        return (f'RunConfig: model={self.chat_model_name}, '
                f'max_result_per_query={self.app_config.max_results_per_query}, '
                f'chat_file={self.chat_file}, chat_template={self.chat_template}')