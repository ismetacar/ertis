import datetime
import json

import jwt
from bson import ObjectId
from jwt import ExpiredSignatureError

from src.utils.errors import ErtisError
from src.generics.service import ErtisGenericService
from src.utils import temporal_helpers
from src.utils.json_helpers import bson_to_json
from passlib.hash import bcrypt


def _get_exp(token_ttl):
    exp_range = datetime.timedelta(minutes=token_ttl)
    return temporal_helpers.to_timestamp(
        (temporal_helpers.utc_now() + exp_range)
    )


def generate_token(payload, secret, token_ttl):
    payload.update({
        'exp': _get_exp(token_ttl),
        'jti': str(ObjectId()),
        'iat': temporal_helpers.to_timestamp(temporal_helpers.utc_now())
    })
    return jwt.encode(payload=payload, key=secret, algorithm='HS256').decode('utf-8')


class ErtisTokenService(ErtisGenericService):

    def craft_token(self, credentials, secret, token_ttl):
        user = self.find_one_by(
            where={
                'email': credentials['email']
            },
            collection='users'
        )

        if not bcrypt.verify(credentials["password"], user["password"]):
            raise ErtisError(
                status_code=403,
                err_code="errors.wrongUsernameOrPassword",
                err_msg="Password mismatch"
            )

        payload = {
            'prn': str(user['_id']),
        }

        payload = json.loads(json.dumps(payload, default=bson_to_json))
        token = generate_token(payload, secret, token_ttl)

        return token

    @staticmethod
    def refresh_token(user, secret, token_ttl):

        payload = {
            "prn": str(user["_id"]),
            "client_id": user['client_id']
        }
        return generate_token(payload, secret, token_ttl)
