import json
import traceback

from flask import request, Response
from sentry_sdk import capture_exception

from src.utils.errors import ErtisError
from src.utils.json_helpers import bson_to_json


def init_additions(app, settings):
    @app.before_request
    def before_request_hook():
        if request.routing_exception:
            raise ErtisError(
                err_msg=request.routing_exception.description,
                err_code="errors.routeExceptionError",
                status_code=request.routing_exception.code
            )

        auth_header = request.headers.get('Authorization', None)

        if request.endpoint not in app.public_endpoints or auth_header:
            token = ensure_token_provided(auth_header)[1]

            user = app.security_manager.load_user(token, settings['application_secret'], settings['verify_token'])
            user['token'] = token
            user['token_type'] = auth_header[0]
            setattr(request, 'user', user)

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

            if settings["sentry"] and status_code == 500:
                capture_exception(error)

            return Response(
                json.dumps(response, default=bson_to_json), status_code,
                mimetype='application/json'
            )


def ensure_token_provided(auth_header):
    if not auth_header:
        raise ErtisError(
            err_code="errors.authorizationHeaderRequired",
            err_msg="Authorization header is required for using this api<{}>",
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

    return auth_header
