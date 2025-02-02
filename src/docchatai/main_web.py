import logging.config

import jinja2.utils
from flask import render_template, request

from docchatai.app.app import App
from docchatai.app.doc_loader import UnsupportedFileTypeError
from docchatai.app.web_data import ValidationError, WebData, WebVar
from docchatai.app.web_app import web_app
from docchatai.app.web_service import WebService


INDEX_TEMPLATE = 'index.html'

app_config = web_app.config['app_config']
web_service: WebService = web_app.config['web_service']

logging.config.dictConfig(app_config.logging_config)

@web_app.template_filter('url_quote')
def url_quote_filter(s):
    return jinja2.utils.url_quote(s)

@web_app.errorhandler(ValidationError)
def handle_validation_error(e):
    return render_template(INDEX_TEMPLATE, **web_service.index({"error": e.message})), 400

@web_app.errorhandler(UnsupportedFileTypeError)
def handle_validation_error(e):
    return render_template(INDEX_TEMPLATE, **web_service.index({"error": e.message})), 400

@web_app.route('/')
def index():
    return render_template(INDEX_TEMPLATE, **web_service.index())

@web_app.route('/chat/model')
def chat_model():
    return render_template(INDEX_TEMPLATE, **web_service.index({"error": "Not yet implemented!"}))

@web_app.route('/chat/file/select')
def chat_file_select():
    chat_file = WebData.get(request, WebVar.CHAT_FILE.value)
    if not chat_file:
        return render_template(INDEX_TEMPLATE, **web_service.index({"error": "No file selected"}))
    return render_template(INDEX_TEMPLATE, **web_service.index({"error": "Not yet implemented!"}))

@web_app.route('/chat/file/upload', methods=['POST'])
def chat_file_upload():
    form_data = WebData.collect_request_form(request)

    response_data = web_service.chat_file_upload(form_data, request.files)

    WebData.update_session(response_data)

    return render_template(INDEX_TEMPLATE, **web_service.index(response_data))

@web_app.route('/chat/file/upload/progress')
def chat_file_upload_progress():
    return str(web_service.chat_file_upload_progress(WebData.get_session_id()))

@web_app.route('/chat/request')
def chat_request():

    form_data = WebData.collect_request_form(request)

    response_data = web_service.chat_request(form_data)

    return render_template(INDEX_TEMPLATE, **web_service.index(response_data))


if __name__ == '__main__':
    try:
        App.init(app_config)

        web_app.run(
            host='0.0.0.0',
            port=app_config.app_port,
            debug=app_config.is_production is False)
    finally:
        App.shutdown()

