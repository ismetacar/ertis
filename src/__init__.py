from flask import Flask
from pymongo import MongoClient


def create_app(settings):
    app = Flask(__name__)

    app.db = MongoClient(settings['mongo_connection_string']).get_database(settings['default_database'])

    from src.services import init_services
    init_services(app, settings)

    from src.rest import register_api
    register_api(app, settings)

    return app
