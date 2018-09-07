import copy
import datetime
import json

from jsonschema import validate, ValidationError

from src.resources.users.users import delete_critical_fields
from src.utils.errors import ErtisError
from src.generics.repository import ErtisGenericRepository, run_function_pool
from src.utils.json_helpers import object_hook, bson_to_json


class ErtisGenericService(ErtisGenericRepository):

    def get(self, _id, resource_name):
        resource = self.find_one_by_id(_id, resource_name)
        return json.dumps(resource, default=bson_to_json)

    def post(self, user, data, resource_name, validate_by=None, before_create=None, after_create=None):
        resource = object_hook(json.loads(data))
        if validate_by:
            try:
                validate(resource, validate_by)
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

        run_function_pool(
            before_create,
            resource=resource,
            user=user,
            generic_service=self,
            resource_name=resource_name,
            _resource=resource,
            data=data
        )

        resource['_sys'] = {
            'created_by': user['email'],
            'created_at': datetime.datetime.utcnow(),
            'collection': resource_name
        }
        resource = self.save(resource, resource_name)

        run_function_pool(
            after_create,
            resource=resource,
            user=user,
            generic_service=self,
            resource_name=resource_name,
            _resource=resource,
            data=data
        )

        return json.dumps(resource, default=bson_to_json)

    def put(self, user, _id, data, resource_name, validate_by=None, before_update=None, after_update=None):
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

        run_function_pool(
            before_update,
            resource=resource,
            user=user,
            generic_service=self,
            resource_name=resource_name,
            _resource=_resource,
            data=data
        )

        resource['_sys'].update({
            'modified_by': user['email'],
            'modified_at': datetime.datetime.utcnow()
        })

        self.replace(
            resource,
            collection=resource_name
        )

        run_function_pool(
            after_update,
            resource=resource,
            user=user,
            generic_service=self,
            resource_name=resource_name,
            data=data,
            _resource=_resource
        )

        return json.dumps(resource, default=bson_to_json)

    def delete(self, user, _id, resource_name, before_delete=None, after_delete=None):
        resource = self.find_one_by_id(_id, collection=resource_name)

        run_function_pool(
            before_delete,
            resource=resource,
            user=user,
            resource_name=resource_name,
            resource_id=_id,
            generic_service=self,
            _resource=resource
        )

        self.remove_one_by_id(_id, collection=resource_name)

        run_function_pool(
            after_delete,
            resource=resource,
            user=user,
            resource_name=resource_name,
            resource_id=_id,
            generic_service=self,
            _resource=resource,
        )

    def filter(self, where, select, limit, sort, skip, resource_name):
        resources, count = self.query(where, select, limit, sort, skip, collection=resource_name)

        response = {
            'items': resources,
            'count': resources
        }

        return json.dumps(response, default=bson_to_json)
