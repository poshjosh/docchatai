import logging
import os
from datetime import datetime
from typing import Union

from pyu.io.file import create_file
from werkzeug.datastructures import ImmutableMultiDict

from docchatai.app.utils import safe_unique_path_name

logger = logging.getLogger(__name__)


def _get_upload_file(uploads_dir: str, task_id: str, filename: str) -> str:
    if not task_id:
        raise ValueError('task id is required')
    if not filename:
        raise ValueError('file name is required')
    now = datetime.now()
    return os.path.join(uploads_dir,
                        now.strftime("%Y"),
                        now.strftime("%m"),
                        now.strftime("%d"),
                        task_id,
                        filename)


def _save_file(uploads_dir: str, session_id: str, input_name: str, uploaded_file) -> Union[str, None]:
    if not uploaded_file:
        return None
    if not uploaded_file.filename:
        return None
    filepath = _get_upload_file(uploads_dir, session_id, safe_unique_path_name(uploaded_file.filename))
    logger.debug(f"Will save: {input_name} to {filepath}")
    create_file(filepath)
    uploaded_file.save(filepath)
    return filepath


def save_files(uploads_dir, session_id, files: ImmutableMultiDict) -> dict[str, any]:
    saved_files = {}
    input_names = files.keys()
    for input_name in input_names:
        saved_file = _save_file(uploads_dir, session_id, input_name, files.get(input_name))
        if not saved_file:
            continue
        saved_files[input_name] = saved_file
    return saved_files
