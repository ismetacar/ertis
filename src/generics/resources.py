from flask import request, Response

from src.utils import query_helpers


class GenericErtisApi(object):
    STATUS_CODE_MAPPING = {
        'CREATE': 201,
        'READ': 200,
        'QUERY': 200,
        'UPDATE': 200,
        'DELETE': 204,
        'DISTINCT': 200
    }

    def __init__(self, app, endpoint_prefix, methods, resource_name, resource_service, create_validation_schema,
                 update_validation_schema, pipeline_functions=None):
        self.app = app
        self.current_app = app
        self.endpoint_prefix = endpoint_prefix
        self.methods = methods
        self.resource_name = resource_name
        self.resource_service = resource_service
        self.create_validation_schema = create_validation_schema
        self.update_validation_schema = update_validation_schema
        self.pipeline_functions = pipeline_functions

    def generate_urls(self):
        delete_url = get_url = update_url = self.endpoint_prefix + '/<resource_id>'
        post_url = self.endpoint_prefix
        query_url = self.endpoint_prefix + '/_query'

        return get_url, post_url, update_url, delete_url, query_url

    def generate_endpoints(self):
        app = self.current_app
        get_url, post_url, update_url, delete_url, query_url = self.generate_urls()

        if 'QUERY' in self.methods:
            @app.route(query_url, methods=['POST'])
            def query():
                where, select, limit, sort, skip = query_helpers.parse(request)
                return Response(
                    self.resource_service.filter(app.generic_service, where, select, limit, skip, sort,
                                                 self.resource_name),
                    mimetype='application/json',
                    status=self.STATUS_CODE_MAPPING['QUERY']
                )

        if 'GET' in self.methods:
            @app.route(get_url, methods=['GET'])
            def read(resource_id):
                return Response(
                    self.resource_service.get(app.generic_service, _id=resource_id, resource_name=self.resource_name),
                    mimetype='application/json',
                    status=self.STATUS_CODE_MAPPING['READ']
                )

        if 'POST' in self.methods:
            @app.route(post_url, methods=['POST'])
            def create():
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
            def update(resource_id):
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
            def delete(resource_id):
                return Response(
                    self.resource_service.delete(
                        app.generic_service,
                        resource_id,
                        resource_name=self.resource_name,
                        pipeline=self.pipeline_functions
                    ),
                    status=self.STATUS_CODE_MAPPING['DELETE']
                )
