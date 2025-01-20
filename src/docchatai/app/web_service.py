import json
import logging

from .chat_service import ChatService, ChatAI
from .config import AppConfig, ChatConfig
from .doc_loader import DocLoader
from .file_service import FileService, UploadedFile
from .web_data import WebVar, WebData, ValidationError

logger = logging.getLogger(__name__)

class WebService:
    def __init__(self, app_config: AppConfig, chat_service: ChatService, file_service: FileService):
        self.__app_config = app_config
        self.default_page_variables = {
            WebVar.APP_NAME.value: app_config.app_name,
            WebVar.TITLE.value: app_config.app_title,
            WebVar.HEADING.value: app_config.app_title,
            WebVar.SUPPORTED_CHAT_FILE_TYPES.value: DocLoader.get_supported_file_extensions(),
            WebVar.CHAT_MODELS.value: ChatService.get_chat_models()
        }
        self.__chat_service = chat_service
        self.__file_service = file_service

    def index(self, web_data: dict[str, any] = None) -> dict[str, str]:
        logger.debug('index, web_data: %s', web_data)
        return self._with_default_page_variables(web_data)

    def chat_file_upload(self, web_data: dict[str, any], files) -> dict[str, any]:
        logger.debug('chat_file_upload\nfiles: %s\nweb_data: %s', files, web_data)

        session_id = web_data[WebVar.SESSION_ID.value]

        saved_files: [UploadedFile] = self.__file_service.save_files(session_id, files)
        for saved_file in saved_files:
            web_data[saved_file.name] = saved_file.to_dict()

        chat_config = ChatConfig(self.__app_config, web_data)

        chat_ai = self.__chat_service.add_chat_ai(session_id, chat_config, False)

        web_data[WebVar.CHAT_MODEL] = {'name': chat_ai.get_model().name }

        return self._with_default_page_variables(web_data)

    def chat_file_upload_progress(self, session_id: str) -> str:
        logger.debug('chat_file_upload_progress, session_id: %s', session_id)

        chat_ai: ChatAI or None = self.__chat_service.get_chat_ai(session_id)

        loaded_pages = -1 if chat_ai is None else chat_ai.get_loader().get_loaded_pages()
        total_pages = -1 if chat_ai is None else chat_ai.get_loader().get_total_pages()

        return json.dumps({"progress": loaded_pages, "total": total_pages})

    def chat_request(self, web_data: dict[str, any]) -> dict[str, any]:
        logger.debug('chat_request, web_data: %s', web_data)

        chat_config = ChatConfig(self.__app_config, web_data)

        request = web_data.get(WebVar.REQUEST.value, None)
        if not request:
            raise ValidationError('Chat message text is required')

        chats = self.__chat_service.chat_request(WebData.get_session_id(), request, chat_config)

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
