import datetime
import json

from flask import request, Response
from jsonschema import validate, ValidationError
from slugify import slugify

from src.generics.repository import maybe_object_id
from src.resources.clients.clients import CREATE_CLIENT_SCHEMA, create_project, create_default_permission_groups
from src.utils.errors import ErtisError
from src.utils.json_helpers import bson_to_json


def init_api(app, settings):
    @app.route('/api/v1/clients', methods=['POST'])
    def create_client():
        auth_header = request.headers.get('Authorization')
        app_secret = settings['application_secret']

        if auth_header.split(' ')[1] != 'Client' and auth_header.split(' ')[1] != app_secret:
            raise ErtisError(
                err_msg="Provided authorization header is invalid",
                err_code="errors.secretIsNotValidForCreateMembership",
                status_code=401
            )

        data = json.loads(request.data)

        try:
            validate(data, CREATE_CLIENT_SCHEMA)
        except ValidationError as e:
            raise ErtisError(
                err_code="errors.invalidJsonProvided",
                err_msg="Invalid json body provided",
                status_code=400,
                context={
                    'message': e.schema.get('required', str(e)),
                    'required': e.schema.get('required', [])
                }
            )

        try:
            data['_id'] = slugify(data['_id'])
        except Exception as e:
            raise ErtisError(
                err_msg="Provided _id is invalid for slugify",
                err_code="errors.invalidIdProvided",
                status_code=400,
                context={
                    'message': str(e)
                }
            )

        data.update({
            '_sys': {
                'created_at': datetime.datetime.utcnow(),
                'created_by': 'system',
                'collection': 'clients'
            }
        })

        client = app.db.clients.save(data)

        project = create_project(client, app.db)
        permission_groups = create_default_permission_groups(client, app.db)
        client = app.db.clients.find_one({
            '_id': client
        })
        project = app.db.projects.find_one({
            '_id': maybe_object_id(project)
        })

        _permission_groups = []
        for permission_group in permission_groups:
            _permission_groups.append(app.db.permission_groups.find_one({
                '_id': maybe_object_id(permission_group)
            }))

        response = {
            'client': client,
            'project': project,
            'permission_groups': _permission_groups
        }

        return Response(
            json.dumps(response, default=bson_to_json),
            mimetype='application/json',
            status=201
        )
