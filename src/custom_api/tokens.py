import json

from flask import request, Response
from jsonschema import validate, ValidationError

from src.custom_models.tokens.schema import CREATE_TOKEN_SCHEMA
from src.custom_models.tokens.tokens import ErtisTokenService
from src.utils.errors import ErtisError


def init_api(app, settings):
    @app.route('/api/tokens', methods=['POST'])
    def create_token():
        body = json.loads(request.data)
        try:
            validate(body, CREATE_TOKEN_SCHEMA)
        except ValidationError as e:
            raise ErtisError(
                err_code="errors.validationError",
                err_msg=str(e.message),
                status_code=400,
                context={
                    'required': e.schema.get('required', []),
                    'properties': e.schema.get('properties', {})
                }
            )

        credentials = {
            'email': body['email'],
            'password': body['password']
        }

        token = ErtisTokenService.craft_token(app.generic_service, credentials)

        response = {
            'token': token
        }

        return Response(json.dumps(response), mimetype='application/json', status=200)


