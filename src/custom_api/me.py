from flask import request, Response

from src.custom_models.me.me import ErtisMeService
from src.custom_models.tokens.tokens import validate_token
from src.utils.errors import ErtisError


def init_api(app, settings):
    @app.route('/api/{}/me'.format(settings['api_version']), methods=['GET'])
    def me():
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

        decoded_token = validate_token(token, settings['application_secret'], settings['verify_token'])

        return Response(
            ErtisMeService.get_user(app.generic_service, decoded_token),
            mimetype='application/json',
            status=200
        )
