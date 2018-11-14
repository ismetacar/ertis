import json
import logging

from flask import request, Response

from src.generics.service import run_read_formatter
from src.resources.security import ErtisSecurityManager
from src.utils import query_helpers
from src.utils.errors import ErtisError


def rename(new_name):
    def wrapper(f):
        f.__name__ = new_name
        return f

    return wrapper


def load_user(db, req, resource_name, settings):
    user = ensure_token_provided(
        db,
        req, resource_name,
        settings['application_secret'], settings['verify_token']
    )
    return user


def ensure_token_provided(db, req, api_name, secret, verify):
    auth_header = req.headers.get('Authorization')
    if not auth_header:
        raise ErtisError(
            err_code="errors.authorizationHeaderRequired",
            err_msg="Authorization header is required for using this api<{}>".format(api_name),
            status_code=401
        )
    try:
        auth_header = auth_header.split(' ')
    except Exception as e:
        ErtisError(
            err_msg="Invalid authorization header provided.",
            err_code="errors.authorizationHeaderIsInvalid",
            status_code=401,
            context={
                'message': str(e)
            }
        )

    if len(auth_header) != 2:
        raise ErtisError(
            err_msg="Bearer token usage is invalid",
            err_code="errors.invalidBearerTokenUsage",
            status_code=401
        )

    token = auth_header[1]
    security_manager = ErtisSecurityManager(db)
    return security_manager.load_user(token, secret, verify)


class GenericErtisApi(object):

    STATUS_CODE_MAPPING = {
        'CREATE': 201,
        'READ': 200,
        'QUERY': 200,
        'UPDATE': 200,
        'DELETE': 204,
        'DISTINCT': 200
    }

    def __init__(self, app, settings, endpoint_prefix, methods, resource_name=None, resource_service=None,
                 create_validation_schema=None, update_validation_schema=None,
                 before_create=None, after_create=None, before_update=None, after_update=None,
                 before_delete=None, after_delete=None, read_formatter=None):
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
        :param create_validation_schema: Validation schemes for POST method
        :param update_validation_schema: Validation schemes for PUT method
        """

        self.app = app
        self.settings = settings
        self.current_app = app
        self.endpoint_prefix = endpoint_prefix
        self.methods = methods
        self.resource_name = resource_name
        self.resource_service = resource_service
        self.create_validation_schema = create_validation_schema
        self.update_validation_schema = update_validation_schema
        self.before_create = before_create
        self.after_create = after_create
        self.before_update = before_update
        self.after_update = after_update
        self.before_delete = before_delete
        self.after_delete = after_delete
        self.read_formatter = read_formatter
        self.logger = logging.getLogger('resource.' + self.resource_name + '.logger')

    def generate_urls(self, *args, **kwargs):

        delete_url = get_url = update_url = self.endpoint_prefix + '/<resource_id>'
        post_url = self.endpoint_prefix
        query_url = self.endpoint_prefix + '/_query'

        if kwargs.get('project_bounded'):
            delete_url = delete_url.format('<project_id>')
            get_url = get_url.format('<project_id>')
            update_url = update_url.format('<project_id>')
            query_url = query_url.format('<project_id>')
            post_url = post_url.format('<project_id>')

        return get_url, post_url, update_url, delete_url, query_url

    def generate_endpoints(self):
        app = self.current_app
        self.logger.info("Resource initialized on <{}> URL".format(self.generate_urls()))

        get_url, post_url, update_url, delete_url, query_url = self.generate_urls()

        if 'QUERY' in self.methods:
            @app.route(query_url, methods=['POST'])
            @rename(self.resource_name + '_query')
            def query():
                load_user(app.db, request, self.resource_name, self.settings)
                where, select, limit, sort, skip = query_helpers.parse(request)
                response = json.loads(self.resource_service.filter(
                        app.generic_service, where, select,
                        limit, sort, skip, self.resource_name
                    ))
                _items = []
                for item in response['items']:
                    item = run_read_formatter(item, self.read_formatter)
                    _items.append(item)

                response['items'] = _items

                return Response(
                    json.dumps(response),
                    mimetype='application/json',
                    status=self.STATUS_CODE_MAPPING['QUERY']
                )

        if 'GET' in self.methods:
            @app.route(get_url, methods=['GET'])
            @rename(self.resource_name + '_read')
            def read(resource_id):
                load_user(app.db, request, self.resource_name, self.settings)
                response = json.loads(self.resource_service.get(
                    app.generic_service,
                    _id=resource_id,
                    resource_name=self.resource_name
                ))
                response = run_read_formatter(response, self.read_formatter)

                return Response(
                    json.dumps(response),
                    mimetype='application/json',
                    status=self.STATUS_CODE_MAPPING['READ']
                )

        if 'POST' in self.methods:
            @app.route(post_url, methods=['POST'])
            @rename(self.resource_name + '_create')
            def create():
                user = load_user(app.db, request, self.resource_name, self.settings)
                data = request.data
                response = json.loads(self.resource_service.post(
                        app.generic_service,
                        user,
                        data,
                        resource_name=self.resource_name,
                        validate_by=self.create_validation_schema,
                        before_create=self.before_create,
                        after_create=self.after_create
                    ))

                response = run_read_formatter(response, self.read_formatter)
                return Response(
                    json.dumps(response),
                    status=self.STATUS_CODE_MAPPING['CREATE'],
                    mimetype='application/json'
                )

        if 'PUT' in self.methods:
            @app.route(update_url, methods=['PUT'])
            @rename(self.resource_name + '_update')
            def update(resource_id):
                user = load_user(app.db, request, self.resource_name, self.settings)
                data = request.data
                response = json.loads(self.resource_service.put(
                        app.generic_service,
                        user,
                        resource_id,
                        data,
                        resource_name=self.resource_name,
                        validate_by=self.update_validation_schema,
                        before_update=self.before_update,
                        after_update=self.after_update
                    ))

                response = run_read_formatter(response, self.read_formatter)
                return Response(
                    json.dumps(response),
                    mimetype='application/json',
                    status=self.STATUS_CODE_MAPPING['UPDATE']
                )

        if 'DELETE' in self.methods:
            @app.route(delete_url, methods=['DELETE'])
            @rename(self.resource_name + '_delete')
            def delete(resource_id):
                user = load_user(app.db, request, self.resource_name, self.settings)
                return Response(
                    self.resource_service.delete(
                        app.generic_service,
                        user,
                        resource_id,
                        resource_name=self.resource_name,
                        before_delete=self.before_delete,
                        after_delete=self.after_delete
                    ),
                    status=self.STATUS_CODE_MAPPING['DELETE']
                )


class ProjectBoundedErtisGenericApi(GenericErtisApi):
    def __init__(self, app, settings, endpoint_prefix, methods, resource_name=None, resource_service=None,
                 create_validation_schema=None, update_validation_schema=None,
                 before_create=None, after_create=None, before_update=None, after_update=None,
                 before_delete=None, after_delete=None):

        super().__init__(app, settings, endpoint_prefix, methods, resource_name=resource_name,
                         resource_service=resource_service, create_validation_schema=create_validation_schema,
                         update_validation_schema=update_validation_schema,
                         before_create=before_create, after_create=after_create, before_update=before_update,
                         after_update=after_update, before_delete=before_delete, after_delete=after_delete)

    def generate_endpoints(self):
        app = self.current_app

        get_url, post_url, update_url, delete_url, query_url = self.generate_urls(project_bounded=True)

        if 'QUERY' in self.methods:
            @app.route(query_url, methods=['POST'])
            @rename(self.resource_name + '_query')
            def query(project_id):
                load_user(app.db, request, self.resource_name, self.settings)
                where, select, limit, sort, skip = query_helpers.parse(request)
                response = json.loads(self.resource_service.filter(
                        app.generic_service, where, select,
                        limit, sort, skip, self.resource_name, project_id
                    ))

                response = run_read_formatter(response, self.read_formatter)

                return Response(
                    json.dumps(response),
                    mimetype='application/json',
                    status=self.STATUS_CODE_MAPPING['QUERY']
                )

        if 'GET' in self.methods:
            @app.route(get_url, methods=['GET'])
            @rename(self.resource_name + '_read')
            def read(project_id, resource_id):
                load_user(app.db, request, self.resource_name, self.settings)
                response = json.loads(self.resource_service.get(
                        app.generic_service,
                        _id=resource_id,
                        resource_name=self.resource_name,
                        project_id=project_id
                    ))

                response = run_read_formatter(response, self.read_formatter)
                return Response(
                    json.dumps(response),
                    mimetype='application/json',
                    status=self.STATUS_CODE_MAPPING['READ']
                )

        if 'POST' in self.methods:
            @app.route(post_url, methods=['POST'])
            @rename(self.resource_name + '_create')
            def create(project_id):
                user = load_user(app.db, request, self.resource_name, self.settings)
                data = request.data
                response = json.loads(self.resource_service.post(
                        app.generic_service,
                        user,
                        data,
                        resource_name=self.resource_name,
                        project_id=project_id,
                        validate_by=self.create_validation_schema,
                        before_create=self.before_create,
                        after_create=self.after_create
                    ))

                response = run_read_formatter(response, self.read_formatter)
                return Response(
                    json.dumps(response),
                    status=self.STATUS_CODE_MAPPING['CREATE'],
                    mimetype='application/json'
                )

        if 'PUT' in self.methods:
            @app.route(update_url, methods=['PUT'])
            @rename(self.resource_name + '_update')
            def update(project_id, resource_id):
                user = load_user(app.db, request, self.resource_name, self.settings)
                data = request.data
                response = json.loads(self.resource_service.put(
                        app.generic_service,
                        user,
                        data,
                        _id=resource_id,
                        project_id=project_id,
                        resource_name=self.resource_name,
                        validate_by=self.update_validation_schema,
                        before_update=self.before_update,
                        after_update=self.after_update
                    ))

                response = run_read_formatter(response, self.read_formatter)
                return Response(
                    json.dumps(response),
                    mimetype='application/json',
                    status=self.STATUS_CODE_MAPPING['UPDATE']
                )

        if 'DELETE' in self.methods:
            @app.route(delete_url, methods=['DELETE'])
            @rename(self.resource_name + '_delete')
            def delete(project_id, resource_id):
                user = load_user(app.db, request, self.resource_name, self.settings)
                return Response(
                    self.resource_service.delete(
                        app.generic_service,
                        user,
                        resource_id,
                        resource_name=self.resource_name,
                        project_id=project_id,
                        before_delete=self.before_delete,
                        after_delete=self.after_delete
                    ),
                    status=self.STATUS_CODE_MAPPING['DELETE']
                )
