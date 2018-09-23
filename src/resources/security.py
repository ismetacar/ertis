import jwt
from jwt import ExpiredSignatureError

from src.generics.service import ErtisGenericService
from src.utils.errors import ErtisError


class ErtisSecurityManager(ErtisGenericService):

    def validate_token(self, token, secret, verify):
        try:
            decoded = jwt.decode(token, key=secret, algorithms='HS256', verify=verify)

        except ExpiredSignatureError as e:
            raise ErtisError(
                status_code=401,
                err_msg="Provided token has expired",
                err_code="errors.tokenExpiredError",
                context={
                    'message': str(e)
                }
            )
        except Exception as e:
            raise ErtisError(
                status_code=401,
                err_msg="Provided token is invalid",
                err_code="errors.tokenIsInvalid",
                context={
                    'e': str(e)
                }
            )

        where = {
            '_id': decoded['prn']
        }
        user = self.find_one_by_id(where, 'users')

        return user

    def load_user(self, token, secret, verify):
        user = self.validate_token(token, secret, verify)

        permission = self.find_one_by(
            where={
                'slug': user['permission_group']
            },
            collection='permission_groups'
        )
        user['permissions'] = permission['permissions']

        client = self.find_one_by(
            where={
                '_id': user['client_id']
            },
            collection='clients'
        )

        user['client'] = client

        return user
