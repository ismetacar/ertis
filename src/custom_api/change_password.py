import json

from flask import request, Response

from passlib.hash import bcrypt
from src.custom_models.tokens.tokens import validate_token
from src.utils.errors import ErtisError
from src.utils.json_helpers import bson_to_json


def init_api(app, settings):
    @app.route('/api/v1/users/<user_id>/change-password', methods=['POST'])
    def change_password(user_id):
        auth_header = request.headers.get('Authorization')
        try:
            body = json.loads(request.data)
        except Exception as e:
            raise ErtisError(
                err_code="errors.invalidBodyProvided",
                err_msg="Provided body is invalid JSON",
                status_code=400,
                context={
                    'message': str(e)
                }
            )

        if not auth_header:
            raise ErtisError(
                err_code="errors.authorizationHeaderRequired",
                err_msg="Authorization header required for use <change_password> api",
                status_code=401
            )

        decoded_token = validate_token(auth_header.split(' ')[1], settings['application_secret'], settings['verify_token'])

        service = app.generic_service
        user = service.find_one_by_id(user_id, 'users')

        if decoded_token['prn'] != str(user['_id']):
            raise ErtisError(
                err_code="errors.userNotAuthorizedForChangePassword",
                err_msg="Users can not change another user's password",
                status_code=403
            )

        new_password = body.get('password', None)
        if len(new_password) < 4:
            raise ErtisError(
                err_msg="Password must be more than 4 characters",
                err_code="errors.passwordIsTooShort",
                status_code=400
            )

        if not new_password:
            raise ErtisError(
                err_msg="Password is required for change password of user",
                err_code="errors.passwordIsRequired",
                status_code=400
            )

        if bcrypt.verify(new_password, user["password"]):
            raise ErtisError(
                err_msg="User's password can not be same with previous password",
                err_code="errors.userPasswordCannotBeSameWithPrevious",
                status_code=400
            )

        hashed_password = bcrypt.hash(new_password)
        user['password'] = hashed_password
        service.replace(user, 'users')

        user.pop('password')

        return Response(json.dumps(user, default=bson_to_json), mimetype='application/json', status=200)