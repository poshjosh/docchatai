import logging
import os
from typing import Union

from pyu.io.file import create_file

from docchatai.app.utils import safe_unique_path_name

logger = logging.getLogger(__name__)

class UploadedFile:
    def __init__(self, name: str, original_filename: str, output_path: str):
        self.name = name
        self.original_filename = original_filename
        self.output_path = output_path

    def to_dict(self) -> dict[str, str]:
        return {
            "name": self.name,
            "original_filename": self.original_filename,
            "output_path": self.output_path
        }

    def __str__(self):
        return f"UploadedFile({self.to_dict()})"

class FileService:
    def __init__(self, output_dir):
        if not output_dir:
            raise ValueError('output dir is required')
        self.__output_dir = output_dir

    def _get_upload_file(self, session_id: str, filename: str) -> str:
        if not session_id:
            raise ValueError('session id is required')
        if not filename:
            raise ValueError('file name is required')
        return os.path.join(self.__output_dir, session_id, filename)

    def list_files(self, session_id: str) -> list[str]:
        if not session_id:
            raise ValueError('session id is required')
        session_dir = os.path.join(self.__output_dir, session_id)
        if not os.path.exists(session_dir):
            return []
        return [os.path.join(session_dir, name) for name in os.listdir(session_dir)]

    def _save_file(self, session_id: str, input_name: str, uploaded_file) -> Union[UploadedFile, None]:
        if not uploaded_file:
            return None
        if not uploaded_file.filename:
            return None
        filepath = self._get_upload_file(session_id, safe_unique_path_name(uploaded_file.filename))
        logger.debug(f"Will save: {input_name} to {filepath}")
        create_file(filepath)
        uploaded_file.save(filepath)
        return UploadedFile(input_name, uploaded_file.filename, filepath)

    def save_files(self, session_id, files: dict[str, any]) -> [UploadedFile]:
        saved_files = []
        input_names = files.keys()
        for input_name in input_names:
            saved_file = self._save_file(session_id, input_name, files.get(input_name))
            if not saved_file:
                continue
            saved_files.append(saved_file)
        return saved_files
