import json

from src.generics.service import ErtisGenericService
from src.utils.json_helpers import bson_to_json


class ErtisMeService(ErtisGenericService):

    def get_user(self, token):
        user = self.find_one_by_id(token['prn'], 'users')
        user.pop('password', None)

        permission_group = user.get('permission_group', None)

        permissions = self.find_one_by(
            where={
                'slug': permission_group
            },
            collection='permission_groups'
        )

        user['permissions'] = permissions['permissions']

        return json.dumps(user, default=bson_to_json)
