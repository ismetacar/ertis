import copy
import json

from jsonschema import validate, ValidationError

from src.custom_models.users.users import delete_critical_fields
from src.utils.errors import ErtisError
from src.generics.repository import ErtisGenericRepository
from src.utils.json_helpers import object_hook, bson_to_json


def run_function_pool(data, pipeline, when=None):
    p_functions = pipeline() if pipeline else {}
    before_create_funcs = p_functions.get(when, [])
    for f in before_create_funcs:
        data = f(data)


class ErtisGenericService(ErtisGenericRepository):

    def get(self, _id, resource_name):
        resource = self.find_one_by_id(_id, resource_name)
        delete_critical_fields(resource)
        return json.dumps(resource, default=bson_to_json)

    def post(self, data, resource_name, validate_by=None, pipeline=None):
        data = object_hook(json.loads(data))
        if validate_by:
            try:
                validate(data, validate_by)
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

        run_function_pool(data, pipeline, when='before_create')
        resource = self.save(data, resource_name)
        run_function_pool(data, pipeline, when='after_create')

        return json.dumps(resource, default=bson_to_json)

    def put(self, _id, data, resource_name, validate_by=None, pipeline=None):
        data = object_hook(json.loads(data))
        if validate_by:
            try:
                validate(data, validate_by)
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

        resource = json.loads(json.dumps(self.find_one_by_id(_id, resource_name), default=bson_to_json))

        _resource = copy.deepcopy(resource)

        resource.update(data)
        if _resource == resource:
            raise ErtisError(
                err_msg="Identical document error",
                err_code="errors.identicalDocumentError",
                status_code=409
            )

        run_function_pool(resource, pipeline, when='before_update')
        self.replace(
            resource,
            collection=resource_name
        )
        run_function_pool(resource, pipeline, when='after_update')

        return json.dumps(resource, default=bson_to_json)

    def delete(self, _id, resource_name, pipeline=None):
        resource = self.find_one_by_id(_id, collection=resource_name)

        run_function_pool(resource, pipeline, when='before_delete')
        self.remove_one_by_id(_id, collection=resource_name)
        run_function_pool(resource, pipeline, when='after_delete')

    def filter(self, where, select, limit, skip, sort, resource_name):
        resources = self.query(where, select, limit, skip, sort, collection=resource_name)

        for resource in resources[0]:
            delete_critical_fields(resource)

        response = {
            'items': resources[0],
            'count': resources[1]
        }

        return json.dumps(response, default=bson_to_json)
