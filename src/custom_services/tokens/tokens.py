import datetime
import json

import jwt
from bson import ObjectId

from src.generics.errors import ErtisError
from src.generics.service import ErtisGenericService
from src.utils import temporal_helpers
from src.utils.json_helpers import bson_to_json
from passlib.hash import bcrypt


def _get_exp():
    exp_range = datetime.timedelta(minutes=15)
    return temporal_helpers.to_timestamp(
        (temporal_helpers.utc_now() + exp_range)
    )


class ErtisTokenService(ErtisGenericService):

    def craft_token(self, credentials):
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
            'exp': _get_exp(),
            'jti': str(ObjectId()),
            'iat': temporal_helpers.to_timestamp(temporal_helpers.utc_now())
        }

        payload = json.loads(json.dumps(payload, default=bson_to_json))

        token = jwt.encode(payload=payload, key='123456789', algorithm='HS256').decode('utf-8')
        return token

