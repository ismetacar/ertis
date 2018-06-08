from src import resources


def register_api(app):

    resources.GenericErtisApi(
        app,
        endpoint_prefix='/api/users',
        methods=['GET', 'POST', 'PUT', 'DELETE', 'QUERY']
    ).generate_endpoints()
