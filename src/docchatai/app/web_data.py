import logging
import uuid
from enum import unique, Enum

from flask import session

from docchatai.app.config import ChatVar

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    def __init__(self, *args):
        super().__init__(*args)
        self.message = args[0]


@unique
class WebVar(str, Enum):
    def __new__(cls, value):
        obj = str.__new__(cls, [value])
        obj._value_ = value
        return obj
    SESSION_ID = 'session_id'
    CHATS = 'chats'
    SUPPORTED_CHAT_FILE_TYPES = 'supported_chat_file_types'
    APP_NAME = 'app_name'
    TITLE = 'title'
    HEADING = 'heading'
    CHAT_FILE = ChatVar.FILE.value
    CHAT_FILES = "chat_files"
    CHAT_MODELS = 'chat_models'
    CHAT_MODEL = 'chat_model'

class WebData:
    @staticmethod
    def get(request, key: str, result_if_none: any = None) -> str or None:
        val = request.args.get(key)
        if not val:
            val = request.form.get(key)
        return result_if_none if not val else val

    @staticmethod
    def get_session_id() -> str:
        session_id = session.get(WebVar.SESSION_ID.value, None)
        if session_id is None:
            session_id = str(uuid.uuid4().hex)
            session[WebVar.SESSION_ID.value] = session_id
        logger.debug('session_id: %s', session_id)
        return session_id

    @staticmethod
    def collect_request_form(request) -> dict[str, any]:
        try:
            web_data = dict(request.form)
            web_data[ChatVar.REQUEST.value] = WebData.get(request, ChatVar.REQUEST.value)
            web_data = WebData.strip_values(web_data)
            web_data[WebVar.SESSION_ID.value] = WebData.get_session_id()
            logger.debug(f"Form data: {web_data}")
            return web_data
        except ValueError as value_ex:
            logger.exception(value_ex)
            raise ValidationError(value_ex.args[0])

    @staticmethod
    def update_session(response_data: dict[str, any]):
        chat_file: dict[str, any] = response_data[ChatVar.FILE.value]
        session[WebVar.CHAT_FILE.value] = chat_file
        session[WebVar.CHAT_MODEL] = response_data[WebVar.CHAT_MODEL]

        chat_files = session.get(WebVar.CHAT_FILES.value, [])
        chat_files.append(chat_file)
        session[WebVar.CHAT_FILES.value] = chat_files

    @staticmethod
    def strip_values(data: dict[str, any]):
        for k, v in data.items():
            v = v.strip() if isinstance(v, str) else v
            data[k] = v
        return data