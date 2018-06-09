from flask import Flask
from pymongo import MongoClient


def create_app():
    app = Flask(__name__)

    client = MongoClient('mongodb://localhost:27017/ertis')
    app.db = client.get_default_database()

    from src.services import init_services
    init_services(app, settings=None)

    from src.rest import register_api
    register_api(app)

    return app