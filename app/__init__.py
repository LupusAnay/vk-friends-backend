import os

from flask import Flask


def create_app(config_name: str = 'app.config.Development') -> Flask:
    app = Flask(__name__)
    config = os.environ.get('APP_SETTINGS', config_name)
    app.config.from_object(config)
    app.config.from_pyfile('config.cfg', silent=True)

    from app.views import auth_blueprint
    app.register_blueprint(auth_blueprint)

    return app
