from src.custom_services.users.schema import CREATE_USER_SCHEMA, UPDATE_USER_SCHEMA
from src.custom_services.users.users import pipeline_functions
from src.generics import resources
from src.generics.service import ErtisGenericService


def register_api(app):

    resources.GenericErtisApi(
        app,
        endpoint_prefix='/api/users',
        methods=['GET', 'POST', 'PUT', 'DELETE', 'QUERY'],
        resource_name='users',
        resource_service=ErtisGenericService,
        create_validation_schema=CREATE_USER_SCHEMA,
        update_validation_schema=UPDATE_USER_SCHEMA,
        pipeline_functions=pipeline_functions
    ).generate_endpoints()
