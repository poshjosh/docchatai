import json
import logging

from .chat_service import ChatService, ChatAI
from .config import AppConfig, ChatConfig
from .doc_loader import DocLoader
from .image_service import save_files
from .web_data import WebVar

logger = logging.getLogger(__name__)

class WebService:
    def __init__(self, app_config: AppConfig, chat_service: ChatService):
        self.__chat_limit = app_config.default_chat_message_limit
        self.__app_config = app_config
        self.default_page_variables = {
            WebVar.APP_NAME.value: app_config.app_name,
            WebVar.TITLE.value: app_config.app_title,
            WebVar.HEADING.value: app_config.app_title,
            WebVar.SUPPORTED_CHAT_FILE_TYPES.value: DocLoader.get_supported_file_extensions(),
            WebVar.CHAT_MODELS.value: ChatService.get_chat_models()
        }
        self.__chat_service = chat_service

    def index(self, web_data: dict[str, any] = None) -> dict[str, str]:
        logger.debug('index, web_data: %s', web_data)
        return self._with_default_page_variables(web_data)

    def chat_file_upload(self, web_data: dict[str, any], files) -> dict[str, any]:
        logger.debug('chat_file_upload\nfiles: %s\nweb_data: %s', files, web_data)

        session_id = web_data[WebVar.SESSION_ID.value]

        web_data.update(save_files(self.__app_config.uploads_dir, session_id, files))

        chat_config = ChatConfig(self.__app_config, web_data)

        chat_ai = self.__chat_service.add_chat_ai(session_id, chat_config, False)

        web_data[WebVar.CHAT_MODEL] = {'name': chat_ai.get_model().name }

        return web_data

    def chat_file_upload_progress(self, session_id: str) -> str:
        logger.debug('chat_file_upload_progress, session_id: %s', session_id)

        chat_ai: ChatAI or None = self.__chat_service.get_chat_ai(session_id)

        loaded_pages = -1 if chat_ai is None else chat_ai.get_loader().get_loaded_pages()
        total_pages = -1 if chat_ai is None else chat_ai.get_loader().get_total_pages()

        return json.dumps({"progress": loaded_pages, "total": total_pages})

    def chat_request(self, web_data: dict[str, any]) -> dict[str, any]:
        logger.debug('chat_request, web_data: %s', web_data)

        chat_config = ChatConfig(self.__app_config, web_data)
        chats = self.__chat_service.chat_request(
            web_data[WebVar.SESSION_ID.value], chat_config, self.__chat_limit)

        #logger.debug('Session chats: %s', chats)

        response_data = {WebVar.CHATS.value: chats}

        return self._with_default_page_variables(response_data)

    def _with_default_page_variables(self, variables: dict[str, any] = None):
        if variables is None:
            variables = {}
        for key, value in self.default_page_variables.items():
            if key not in variables.keys():
                variables[key] = value
        return variables
