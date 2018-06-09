import copy
import json

from src.generics.errors import ErtisError
from src.generics.repository import ErtisGenericRepository
from src.utils.json_helpers import object_hook, bson_to_json


class ErtisGenericService(ErtisGenericRepository):

    def get(self, _id, resource_name):
        user = self.find_one_by_id(_id, resource_name)
        return json.dumps(user, default=bson_to_json)

    def post(self, data, resource_name):
        data = object_hook(json.loads(data))
        user = self.save(data, resource_name)
        return json.dumps(user, default=bson_to_json)

    def put(self, _id, data, resource_name):
        provided_data = object_hook(json.loads(data))
        resource = json.loads(json.dumps(self.find_one_by_id(_id, resource_name), default=bson_to_json))

        _resource = copy.deepcopy(resource)

        resource.update(provided_data)
        if _resource == resource:
            raise ErtisError(
                err_msg="Identical document error",
                err_code="errors.identicalDocumentError",
                status_code=409
            )

        self.update_one_by(
            where={
                '_id': _id
            },
            command={
                '$set': provided_data
            },
            collection=resource_name
        )

        return json.dumps(resource, default=bson_to_json)

    def delete(self, _id, resource_name):
        self.remove_one_by_id(_id, collection=resource_name)
