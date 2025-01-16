import logging
import os
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
            'formatters': {'simple': {'format': '%(asctime)s %(name)s %(levelname)s %(message)s'}},
            'handlers': {'console': {
                'class': 'logging.StreamHandler', 'level': f'{log_level}', 'formatter': 'simple'}},
            'loggers': {'app': {'level': f'{log_level}', 'handlers': ['console'], 'propagate': False}}
        }



class RunConfig(AppConfig):
    def __init__(self):
        super().__init__()
        logger.debug(f'Args: {argv}')

    @property
    def chat_model_provider(self) -> str:
        return os.environ.get('CHAT_MODEL_PROVIDER',
                              argv[1] if len(argv) > 1 else self.default_chat_model_name)

    @property
    def chat_model_name(self) -> str:
        return os.environ.get('CHAT_MODEL',
                              argv[2] if len(argv) > 2 else self.default_chat_model_name)

    @property
    def input_file(self) -> str:
        input_file = os.environ.get('INPUT_FILE', argv[3] if len(argv) > 3 else None)
        if input_file is None:
            raise ValueError('Input file is required')
        return input_file

    @property
    def chat_template(self) -> str:
        return os.environ.get('CHAT_TEMPLATE', self.default_chat_template)

    def __str__(self):
        return (f'RunConfig: model={self.chat_model_name}, '
                f'max_result_per_query={self.max_results_per_query}, input_file={self.input_file}')