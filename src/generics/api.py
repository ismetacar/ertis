import json
import logging

from flask import request, Response

from src.generics.service import run_read_formatter
from src.utils import query_helpers


def rename(new_name):
    def wrapper(f):
        f.__name__ = new_name
        return f

    return wrapper


class GenericErtisApi(object):
    def __init__(self, app, settings, endpoint_prefix, methods, 
                 resource_name=None, resource_service=None, allow_anonymous=False):
        """

        if a generated instance is subjected to generate_endpoints() function, APIs are created for basic HTTP methods

        Usage:

            GenericErtisApi(
                app,
                settings,
                endpoint_prefix='/api/example-endpoint',
                methods=['GET', 'POST', 'PUT', 'DELETE', 'QUERY'],
                resource_name='example',
                resource_service=example-service,
                create_validation_schema=jsonschema_for_create,
                update_validation_schema=jsonschema_for_update,
                pipeline_functions=example_functions
            ).generate_endpoints()

        :param app: The currently running application.
        :param settings: Predefined application settings in config file
        :param endpoint_prefix: Endpoint of the related API
        :param methods: HTTP methods for current API
        :param resource_name: API name and name of the collection in the database
        :param resource_service: Service to be used for related API
        """

        self.app = app
        self.settings = settings
        self.current_app = app
        self.endpoint_prefix = endpoint_prefix
        self.methods = methods
        self.resource_name = resource_name
        self.resource_service = resource_service
        self.allow_anonymous = allow_anonymous

        self.logger = logging.getLogger('resource.' + self.resource_name + '.logger')

    STATUS_CODE_MAPPING = {
        'CREATE': 201,
        'READ': 200,
        'QUERY': 200,
        'UPDATE': 200,
        'DELETE': 204,
        'DISTINCT': 200
    }

    def generate_urls(self):

        delete_url = get_url = update_url = self.endpoint_prefix + '/<resource_id>'
        post_url = self.endpoint_prefix
        query_url = self.endpoint_prefix + '/_query'

        return get_url, post_url, update_url, delete_url, query_url

    def generate_endpoints(
            self,
            create_validation_schema=None,
            update_validation_schema=None,
            before_create=None, after_create=None,
            before_update=None, after_update=None,
            before_delete=None, after_delete=None,
            read_formatter=None
    ):
        self.logger.info("Resource initialized on <{}> URL".format(self.generate_urls()))
        app = self.current_app

        endpoint_determiner = ['_create', '_read', '_update', '_delete', '_query']

        if self.allow_anonymous:
            for determiner in endpoint_determiner:
                app.public_endpoints.append(self.resource_name + determiner)

        get_url, post_url, update_url, delete_url, query_url = self.generate_urls()

        if 'QUERY' in self.methods:
            @app.route(query_url, methods=['POST'], endpoint=self.resource_name + '_query')
            @rename(self.resource_name + '_query')
            def query():

                where, select, limit, sort, skip = query_helpers.parse(request)
                user = getattr(request, 'user', None)

                response = json.loads(self.resource_service.filter(
                    app.generic_service, where=where, select=select, user=user,
                    limit=limit, sort=sort, skip=skip, resource_name=self.resource_name
                ))

                _items = []
                for item in response['items']:
                    item = run_read_formatter(item, read_formatter)
                    _items.append(item)

                response['items'] = _items

                return Response(
                    json.dumps(response),
                    mimetype='application/json',
                    status=self.STATUS_CODE_MAPPING['QUERY']
                )

        if 'GET' in self.methods:
            @app.route(get_url, methods=['GET'], endpoint=self.resource_name + '_read')
            @rename(self.resource_name + '_read')
            def read(resource_id):
                user = getattr(request, 'user', None)

                response = json.loads(self.resource_service.get(
                    app.generic_service,
                    _id=resource_id,
                    resource_name=self.resource_name,
                    user=user
                ))

                response = run_read_formatter(response, read_formatter)

                return Response(
                    json.dumps(response),
                    mimetype='application/json',
                    status=self.STATUS_CODE_MAPPING['READ']
                )

        if 'POST' in self.methods:
            @app.route(post_url, methods=['POST'], endpoint=self.resource_name + '_create')
            @rename(self.resource_name + '_create')
            def create():
                user = getattr(request, 'user', None)
                data = request.data

                response = json.loads(self.resource_service.post(
                    app.generic_service,
                    user=user,
                    data=data,
                    resource_name=self.resource_name,
                    validate_by=create_validation_schema,
                    before_create=before_create,
                    after_create=after_create
                ))

                response = run_read_formatter(response, read_formatter)
                return Response(
                    json.dumps(response),
                    status=self.STATUS_CODE_MAPPING['CREATE'],
                    mimetype='application/json'
                )

        if 'PUT' in self.methods:
            @app.route(update_url, methods=['PUT'], endpoint=self.resource_name + '_update')
            @rename(self.resource_name + '_update')
            def update(resource_id):

                user = getattr(request, 'user', None)
                data = request.data
                response = json.loads(self.resource_service.put(
                    app.generic_service,
                    user=user,
                    resource_id=resource_id,
                    data=data,
                    resource_name=self.resource_name,
                    validate_by=update_validation_schema,
                    before_update=before_update,
                    after_update=after_update
                ))

                response = run_read_formatter(response, read_formatter)
                return Response(
                    json.dumps(response),
                    mimetype='application/json',
                    status=self.STATUS_CODE_MAPPING['UPDATE']
                )

        if 'DELETE' in self.methods:
            @app.route(delete_url, methods=['DELETE'], endpoint=self.resource_name + '_delete')
            @rename(self.resource_name + '_delete')
            def delete(resource_id):

                user = getattr(request, 'user', None)

                return Response(
                    self.resource_service.delete(
                        app.generic_service,
                        user=user,
                        resource_id=resource_id,
                        resource_name=self.resource_name,
                        before_delete=before_delete,
                        after_delete=after_delete
                    ),
                    status=self.STATUS_CODE_MAPPING['DELETE']
                )
