import sentry_sdk
from flask import Flask
from flask_mail import Mail
from pymongo import MongoClient


def create_app(settings):
    app = Flask(__name__, template_folder="../templates/")

    app.db = MongoClient(settings['mongo_connection_string']).get_database(settings['default_database'])
    app.public_endpoints = ['healtcheck', 'create_token', 'site_map']

    if settings['sentry']:
        sentry_sdk.init(settings['sentry_connection_string'])

    if settings['email']:
        app.config['MAIL_SERVER'] = settings['mail_server']
        app.config['MAIL_PORT'] = settings['mail_port']
        app.config['MAIL_USE_TLS'] = False
        app.config['MAIL_USE_SSL'] = True
        app.config['MAIL_USERNAME'] = settings['mail_username']
        app.config['MAIL_PASSWORD'] = settings['mail_password']

        mail = Mail(app)
        app.mail = mail

    from src.services import init_services
    init_services(app, settings)

    from src.rest import register_api
    register_api(app, settings)

    from src.rest import setup_api
    setup_api(app)

    from src.generics.additions import init_additions
    init_additions(app, settings)

    return app
