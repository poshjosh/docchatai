import uuid

from flask import Flask, render_template, request, session
# from flask_cors import CORS
import logging.config

from app.app import App
from app.config import AppConfig
from app.request_data import ValidationError, RequestData
from app.web_service import WebService
from docchatai.app.chat_service import ChatService

web_app = Flask(__name__)
# CORS(web_app)

INDEX_TEMPLATE = 'index.html'


@web_app.errorhandler(ValidationError)
def handle_validation_error(e):
    return render_template(INDEX_TEMPLATE, **web_service.index({"error": e.message})), 400


@web_app.route('/')
def index():
    return render_template(INDEX_TEMPLATE, **web_service.index())


@web_app.route('/chat/request', methods=['POST'])
def chat_request():

    session_id = session.get('session_id', None)
    if session_id is None:
        session_id = str(uuid.uuid4().hex)
        session['session_id'] = session_id

    form_data = RequestData.collect_form_data(session_id, request, app_config.uploads_dir, [])

    page_variables = web_service.chat_request(session_id, form_data)

    return render_template(INDEX_TEMPLATE, **web_service.index(page_variables))


if __name__ == '__main__':

    app_config = AppConfig()
    logging.config.dictConfig(app_config.logging_config)

    try:
        App.init(app_config)

        web_service = WebService(app_config, ChatService())

        web_app.secret_key = app_config.secret_key
        web_app.run(
            host='0.0.0.0',
            port=app_config.app_port,
            debug=app_config.is_production is False)
    finally:
        App.shutdown()

