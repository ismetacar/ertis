from flask import Flask
from pymongo import MongoClient


def create_app(settings):
    app = Flask(__name__)

    client = MongoClient(settings['mongo_connection_string'])
    app.db = client.get_default_database()

    from src.services import init_services
    init_services(app, settings)

    from src.rest import register_api
    register_api(app, settings)

    return app