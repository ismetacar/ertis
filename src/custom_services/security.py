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

        user = self.find_one_by_id(decoded['prn'], 'users')

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

        return user
