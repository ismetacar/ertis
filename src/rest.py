from src import resources
from src.generics.service import ErtisGenericService


def register_api(app):

    resources.GenericErtisApi(
        app,
        endpoint_prefix='/api/users',
        methods=['GET', 'POST', 'PUT', 'DELETE', 'QUERY'],
        resource_name='users',
        resource_service=ErtisGenericService
    ).generate_endpoints()
