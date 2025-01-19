from flask import Flask

from docchatai.app.config import AppConfig
from docchatai.app.web_service import WebService
from docchatai.app.chat_service import ChatService

def create_web_app(app_config: AppConfig = AppConfig(),
                   static_folder='../static',
                   template_folder='../templates') -> Flask:
    app = Flask(__name__, static_folder=static_folder, template_folder=template_folder)
    app.secret_key = app_config.secret_key

    # from flask_cors import CORS
    # CORS(app)

    app.config['app_config'] = app_config
    app.config['web_service'] = WebService(app_config, ChatService())

    return app

web_app = create_web_app()
