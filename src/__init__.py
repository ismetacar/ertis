from flask import Flask
from pymongo import MongoClient
import sentry_sdk


def create_app(settings):
    app = Flask(__name__)

    sentry_sdk.init(settings['sentry_connection_string'])
    app.db = MongoClient(settings['mongo_connection_string']).get_database(settings['default_database'])
    app.public_endpoints = ['healtcheck', 'create_token', 'site_map']

    from src.services import init_services
    init_services(app, settings)

    from src.rest import register_api
    register_api(app, settings)

    from src.rest import setup_api
    setup_api(app)

    from src.generics.additions import init_additions
    init_additions(app, settings)

    return app
