import json
import optparse
import os
import traceback

from flask import Response

from confs.development import development_config
from confs.local import local_config
from confs.production import production_config
from src import create_app
from src.resources.security import ErtisSecurityManager
from src.utils.errors import ErtisError
from src.utils.json_helpers import bson_to_json, parse_boolean

CONFIG_LOOKUP = {
    'local': local_config,
    'development': development_config,
    'production': production_config
}

parser = optparse.OptionParser()

parser.add_option("--config", default="local")


def config_settings():
    options, _ = parser.parse_args()
    return CONFIG_LOOKUP[options.config]


settings = config_settings()

app = create_app(settings)
app.security_manager = ErtisSecurityManager(app.db)

app.debug = settings['debug']
app.secret_key = settings['application_secret']
app.port = settings['port']

if settings.get('error_handler', False):

    @app.errorhandler(Exception)
    def handle_exceptions(error):
        if isinstance(error, ErtisError):
            response = {
                'err_msg': error.err_msg or 'Internal error occurred',
                'err_code': error.err_code or 'errors.internalError',
                'context': error.context,
                'reason': error.reason
            }
            status_code = error.status_code

        else:
            response = {
                'err_msg': str(error),
                'err_code': "errors.internalError",
                'traceback': str(traceback.extract_stack())
            }
            status_code = getattr(error, 'code', 500)

        return Response(
            json.dumps(response, default=bson_to_json), status_code,
            mimetype='application/json'
        )

if __name__ == '__main__':
    app.run(port=app.port)
