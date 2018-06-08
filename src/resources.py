from flask import jsonify


class GenericErtisApi(object):
    def __init__(self, app, endpoint_prefix, methods):
        self.app = app
        self.current_app = app
        self.endpoint_prefix = endpoint_prefix
        self.methods = methods

    def generate_urls(self):
        delete_url = get_url = update_url = self.endpoint_prefix + '/<resource_id>'
        post_url = self.endpoint_prefix
        query_url = self.endpoint_prefix + '/_query'

        return get_url, post_url, update_url, delete_url, query_url

    def generate_endpoints(self):
        app = self.current_app
        get_url, post_url, update_url, delete_url, query_url = self.generate_urls()

        if 'GET' in self.methods:
            @app.route(get_url, methods=['GET'])
            def read(resource_id):
                return jsonify({
                    'resource_id': resource_id,
                    'username': 'ismetacar',
                    'method': self.methods
                })

        if 'POST' in self.methods:
            @app.route(post_url, methods=['POST'])
            def create(resource_id):
                pass

        if 'PUT' in self.methods:
            @app.route(update_url, methods=['PUT'])
            def update(resource_id):
                pass

        if 'DELETE' in self.methods:
            @app.route(delete_url, methods=['DELETE'])
            def delete(resource_id):
                pass

        if 'QUERY' in self.methods:
            @app.route(query_url, methods=['GET'])
            def query(resource_id):
                pass
