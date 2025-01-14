import logging
import os
from datetime import datetime
from sys import argv

logger = logging.getLogger(__name__)

class AppConfig:
    @property
    def app_dir(self) -> str:
        return os.environ['APP_DIR']

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
    def default_chat_template(self) -> str:
        return """
            You are an information retrieval AI.
            You will provide a relevant response to the request.
            Your response should be based only on the context provided.
            Do not make up any information.
            
            Request: {request}
            
            Context: {context}
        """


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