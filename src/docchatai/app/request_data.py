import logging
from typing import Union

from .image_service import save_files

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    def __init__(self, *args):
        super().__init__(*args)
        self.message = args[0]

class RequestData:
    @staticmethod
    def get(request, key: str, result_if_none: any = None) -> Union[str, None]:
        val = request.args.get(key)
        if not val:
            val = request.form.get(key)
        return result_if_none if not val else val

    @staticmethod
    def collect_form_data(session_id: str, request, uploads_dir: str, file_input_names: [str]) -> dict[str, any]:
        try:
            form_data = dict(request.form)
            form_data.update(save_files(uploads_dir, session_id, request.files, file_input_names))
            form_data = RequestData.strip_values(form_data)
            logger.debug(f"Form data: {form_data}")
            return form_data
        except ValueError as value_ex:
            logger.exception(value_ex)
            raise ValidationError(value_ex.args[0])

    @staticmethod
    def strip_values(data: dict[str, any]):
        for k, v in data.items():
            v = v.strip() if isinstance(v, str) else v
            data[k] = v
        return data