import logging

from flask import request, Response

from src.custom_models.tokens.tokens import validate_token
from src.utils import query_helpers
from src.utils.errors import ErtisError


def rename(new_name):
    def decorator(f):
        f.__name__ = new_name
        return f

    return decorator


def ensure_token_provided(req, api_name, secret):
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

    validate_token(token, secret)


class GenericErtisApi(object):
    STATUS_CODE_MAPPING = {
        'CREATE': 201,
        'READ': 200,
        'QUERY': 200,
        'UPDATE': 200,
        'DELETE': 204,
        'DISTINCT': 200
    }

    def __init__(self, app, settings, endpoint_prefix, methods, resource_name, resource_service,
                 create_validation_schema=None, update_validation_schema=None, pipeline_functions=None,
                 allow_to_anonymous=False):
        self.app = app
        self.settings = settings
        self.current_app = app
        self.endpoint_prefix = endpoint_prefix
        self.methods = methods
        self.resource_name = resource_name
        self.resource_service = resource_service
        self.create_validation_schema = create_validation_schema
        self.update_validation_schema = update_validation_schema
        self.pipeline_functions = pipeline_functions
        self.allow_to_anonymous = allow_to_anonymous
        self.logger = logging.getLogger('resource.' + self.resource_name + '.logger')

    def generate_urls(self):
        delete_url = get_url = update_url = self.endpoint_prefix + '/<resource_id>'
        post_url = self.endpoint_prefix
        query_url = self.endpoint_prefix + '/_query'

        return get_url, post_url, update_url, delete_url, query_url

    def generate_endpoints(self):
        app = self.current_app
        self.logger.info("Resource initialized on <{}> URL".format(self.generate_urls()))

        get_url, post_url, update_url, delete_url, query_url = self.generate_urls()

        if 'QUERY' in self.methods:
            @app.route(query_url, methods=['POST'])
            @rename(self.resource_name + '_query')
            def query():
                if not self.allow_to_anonymous:
                    ensure_token_provided(request, self.resource_name, self.settings['application_secret'])
                where, select, limit, sort, skip = query_helpers.parse(request)
                return Response(
                    self.resource_service.filter(
                        app.generic_service, where, select,
                        limit, skip, sort, self.resource_name
                    ),
                    mimetype='application/json',
                    status=self.STATUS_CODE_MAPPING['QUERY']
                )

        if 'GET' in self.methods:
            @app.route(get_url, methods=['GET'])
            @rename(self.resource_name + '_read')
            def read(resource_id):
                if not self.allow_to_anonymous:
                    ensure_token_provided(request, self.resource_name, self.settings['application_secret'])
                return Response(
                    self.resource_service.get(
                        app.generic_service,
                        _id=resource_id,
                        resource_name=self.resource_name
                    ),
                    mimetype='application/json',
                    status=self.STATUS_CODE_MAPPING['READ']
                )

        if 'POST' in self.methods:
            @app.route(post_url, methods=['POST'])
            @rename(self.resource_name + '_create')
            def create():
                if not self.allow_to_anonymous:
                    ensure_token_provided(request, self.resource_name, self.settings['application_secret'])
                data = request.data
                return Response(
                    self.resource_service.post(
                        app.generic_service,
                        data,
                        resource_name=self.resource_name,
                        validate_by=self.create_validation_schema,
                        pipeline=self.pipeline_functions
                    ),
                    status=self.STATUS_CODE_MAPPING['CREATE'],
                    mimetype='application/json'
                )

        if 'PUT' in self.methods:
            @app.route(update_url, methods=['PUT'])
            @rename(self.resource_name + '_update')
            def update(resource_id):
                if not self.allow_to_anonymous:
                    ensure_token_provided(request, self.resource_name, self.settings['application_secret'])
                data = request.data
                return Response(
                    self.resource_service.put(
                        app.generic_service,
                        resource_id,
                        data,
                        resource_name=self.resource_name,
                        validate_by=self.update_validation_schema,
                        pipeline=self.pipeline_functions
                    ),
                    mimetype='application/json',
                    status=self.STATUS_CODE_MAPPING['UPDATE']
                )

        if 'DELETE' in self.methods:
            @app.route(delete_url, methods=['DELETE'])
            @rename(self.resource_name + '_delete')
            def delete(resource_id):
                if not self.allow_to_anonymous:
                    ensure_token_provided(request, self.resource_name, self.settings['application_secret'])
                return Response(
                    self.resource_service.delete(
                        app.generic_service,
                        resource_id,
                        resource_name=self.resource_name,
                        pipeline=self.pipeline_functions
                    ),
                    status=self.STATUS_CODE_MAPPING['DELETE']
                )
