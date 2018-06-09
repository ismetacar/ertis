from src.custom_models.users.schema import CREATE_USER_SCHEMA, UPDATE_USER_SCHEMA
from src.custom_models.users.users import pipeline_functions
from src.generics import api
from src.generics.service import ErtisGenericService


def register_api(app):

    api.GenericErtisApi(
        app,
        endpoint_prefix='/api/users',
        methods=['GET', 'POST', 'PUT', 'DELETE', 'QUERY'],
        resource_name='users',
        resource_service=ErtisGenericService,
        create_validation_schema=CREATE_USER_SCHEMA,
        update_validation_schema=UPDATE_USER_SCHEMA,
        pipeline_functions=pipeline_functions,
        allow_to_anonymous=False
    ).generate_endpoints()
