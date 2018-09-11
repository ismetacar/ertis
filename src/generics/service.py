import copy
import datetime
import json
from pprint import pprint

from jsonschema import validate, ValidationError

from src.generics.repository import ErtisGenericRepository, run_function_pool
from src.utils.errors import ErtisError
from src.utils.json_helpers import object_hook, bson_to_json


class ErtisGenericService(ErtisGenericRepository):

    def get(self, _id, resource_name, project_id=None):
        where = {'_id': _id}

        if project_id:
            where.update({'project_id': project_id})

        resource = self.find_one_by_id(where, resource_name)
        return json.dumps(resource, default=bson_to_json)

    def post(self, user, data, resource_name, project_id=None, validate_by=None, before_create=None, after_create=None):
        resource = object_hook(json.loads(data))
        resource.update({
            'client_id': user['client_id']
        })

        if project_id:
            resource.update({'project_id': project_id})

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

        if before_create:
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

        if after_create:
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

    def put(self, user, _id, data, resource_name, validate_by=None, before_update=None,
            after_update=None, project_id=None):

        try:
            data = object_hook(json.loads(data))
        except Exception as e:
            pprint(str(e))

        data.update({
            'client_id': user['client_id'],
        })

        if project_id:
            data.update({'project_id': project_id})

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

        where = {
            '_id': _id
        }

        if project_id:
            data.update({'project_id': project_id})

        resource = json.loads(json.dumps(self.find_one_by_id(where, resource_name), default=bson_to_json))

        _resource = copy.deepcopy(resource)

        resource.update(data)
        if _resource == resource:
            raise ErtisError(
                err_msg="Identical document error",
                err_code="errors.identicalDocumentError",
                status_code=409
            )

        if before_update:
            run_function_pool(
                before_update,
                resource=resource,
                user=user,
                project_id=project_id,
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

        if after_update:
            run_function_pool(
                after_update,
                resource=resource,
                user=user,
                project_id=project_id,
                generic_service=self,
                resource_name=resource_name,
                data=data,
                _resource=_resource
            )

        return json.dumps(resource, default=bson_to_json)

    def delete(self, user, _id, resource_name, project_id=None, before_delete=None, after_delete=None):
        where = {'_id': _id}
        if project_id:
            where.update({'project_id': project_id})

        resource = self.find_one_by_id(where, collection=resource_name)

        if before_delete:
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

        if after_delete:
            run_function_pool(
                after_delete,
                resource=resource,
                user=user,
                resource_name=resource_name,
                resource_id=_id,
                generic_service=self,
                _resource=resource,
            )

    def filter(self, where, select, limit, sort, skip, resource_name, project_id=None):
        if not where:
            where = {}

        if project_id:
            where.update({
                'project_id': project_id
            })

        resources, count = self.query(where, select, limit, sort, skip, collection=resource_name)

        response = {
            'items': resources,
            'count': len(resources)
        }

        return json.dumps(response, default=bson_to_json)


def run_read_formatter(resource, function_pool):
    if not function_pool:
        return resource

    for func in function_pool:
        resource = func(resource)

    return resource
