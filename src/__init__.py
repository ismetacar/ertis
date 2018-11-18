import sentry_sdk
from flask import Flask
from flask_mail import Mail
from pymongo import MongoClient


def create_app(settings):
    app = Flask(__name__, template_folder="../templates/")

    app.db = MongoClient(settings['mongo_connection_string']).get_database(settings['default_database'])
    app.public_endpoints = ['healtcheck', 'create_token', 'site_map']

    if settings['sentry']['active']:
        sentry_sdk.init(settings['sentry']['connection_string'])

    if settings['email']['active']:
        app.config['MAIL_SERVER'] = settings['email']['mail_server']
        app.config['MAIL_PORT'] = settings['email']['mail_port']
        app.config['MAIL_USE_TLS'] = settings['email']['mail_use_tls']
        app.config['MAIL_USE_SSL'] = settings['email']['mail_use_ssl']
        app.config['MAIL_USERNAME'] = settings['email']['mail_username']
        app.config['MAIL_PASSWORD'] = settings['email']['mail_password']

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
