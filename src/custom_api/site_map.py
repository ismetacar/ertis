import json

from flask import request, Response

from src.custom_services.security import ErtisSecurityManager
from src.utils.errors import ErtisError
from src.utils.json_helpers import bson_to_json


def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)


def init_api(app, settings):
    @app.route('/api/{}/api-map'.format(settings['api_version']), methods=['GET'])
    def site_map():
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            raise ErtisError(
                err_code="errors.authorizationHeaderRequired",
                err_msg="Authorization header is required for using ME API",
                status_code=401
            )
        try:
            auth_header = auth_header.split(' ')
        except Exception as e:
            ErtisError(
                err_msg="Invalid authorization header provided.",
                err_code="errors.authorizationHeaderIsInvalid",
                status_code=401,
                context={
                    'message': str(e)
                }
            )

        if len(auth_header) != 2:
            raise ErtisError(
                err_msg="Bearer token usage is invalid",
                err_code="errors.invalidBearerTokenUsage",
                status_code=401
            )

        token = auth_header[1]

        security_manager = ErtisSecurityManager(app.db)
        security_manager.load_user(token, settings['application_secret'], settings['verify_token'])

        links = []
        for rule in app.url_map.iter_rules():
            options = {}
            for arg in rule.arguments:
                options[arg] = "[{0}]".format(arg)

            methods = ','.join(rule.methods)
            url = str(rule)
            if rule.endpoint == 'static':
                continue

            line = "{:50s} {:20s} {}".format(rule.endpoint, methods, url)
            links.append(line)

        return Response(json.dumps(links, default=bson_to_json), mimetype='application/json', status=200)
