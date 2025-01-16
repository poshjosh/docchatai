import logging

from .chat_service import ChatService
from .config import AppConfig

logger = logging.getLogger(__name__)

class WebService:
    def __init__(self, app_config: AppConfig, chat_service: ChatService):
        self.__chat_limit = app_config.default_chat_message_limit
        self.default_page_variables = {
            'app_name': app_config.app_name,
            'title': app_config.app_title,
            'heading': app_config.app_title
        }
        self.__chat_service = chat_service

    def index(self, request_data: dict[str, any] = None) -> dict[str, str]:
        logger.debug('index, request_data: %s', request_data)
        return self._with_default_page_variables(request_data)

    def chat_request(self, session_id: str, request_data: dict[str, any]) -> dict[str, any]:
        logger.debug('chat_request, request_data: %s', request_data)

        chats = self.__chat_service.chat_request(session_id, request_data, self.__chat_limit)

        logger.debug('Session chats: %s', chats)

        response_data = {'chats': chats}

        return self._with_default_page_variables(response_data)

    def _with_default_page_variables(self, variables: dict[str, any] = None):
        if variables is None:
            variables = {}
        for key, value in self.default_page_variables.items():
            if key not in variables.keys():
                variables[key] = value
        return variables
