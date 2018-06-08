from flask import Flask

from src.rest import register_api


def create_app():
    app = Flask(__name__)

    register_api(app)

    return app