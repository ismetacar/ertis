from src.custom_models.users.schema import CREATE_USER_SCHEMA, UPDATE_USER_SCHEMA
from src.custom_models.users.users import pipeline_functions
from src.generics import api
from src.generics.service import ErtisGenericService


def register_api(app, settings):

    api.GenericErtisApi(
        app,
        settings,
        endpoint_prefix='/api/v1/users',
        methods=['GET', 'POST', 'PUT', 'DELETE', 'QUERY'],
        resource_name='users',
        resource_service=ErtisGenericService,
        create_validation_schema=CREATE_USER_SCHEMA,
        update_validation_schema=UPDATE_USER_SCHEMA,
        pipeline_functions=pipeline_functions,
        allow_to_anonymous=False
    ).generate_endpoints()

    api.GenericErtisApi(
        app,
        settings,
        endpoint_prefix='/api/v1/positions',
        methods=['GET', 'POST', 'PUT', 'DELETE', 'QUERY'],
        resource_name='positions',
        resource_service=ErtisGenericService,
        allow_to_anonymous=False
    ).generate_endpoints()

    api.GenericErtisApi(
        app,
        settings,
        endpoint_prefix='/api/v1/user-groups',
        methods=['GET', 'POST', 'PUT', 'DELETE', 'QUERY'],
        resource_name='user_groups',
        resource_service=ErtisGenericService,
        allow_to_anonymous=False
    ).generate_endpoints()

    api.GenericErtisApi(
        app,
        settings,
        endpoint_prefix='/api/v1/departments',
        methods=['GET', 'POST', 'PUT', 'DELETE', 'QUERY'],
        resource_name='departments',
        resource_service=ErtisGenericService,
        allow_to_anonymous=False
    ).generate_endpoints()

    api.GenericErtisApi(
        app,
        settings,
        endpoint_prefix='/api/v1/materials',
        methods=['GET', 'POST', 'PUT', 'DELETE', 'QUERY'],
        resource_name='materials',
        resource_service=ErtisGenericService,
        allow_to_anonymous=False
    ).generate_endpoints()

    api.GenericErtisApi(
        app,
        settings,
        endpoint_prefix='/api/v1/material-types',
        methods=['GET', 'POST', 'PUT', 'DELETE', 'QUERY'],
        resource_name='material_types',
        resource_service=ErtisGenericService,
        allow_to_anonymous=False
    ).generate_endpoints()

    api.GenericErtisApi(
        app,
        settings,
        endpoint_prefix='/api/v1/projects',
        methods=['GET', 'POST', 'PUT', 'DELETE', 'QUERY'],
        resource_name='projects',
        resource_service=ErtisGenericService,
        allow_to_anonymous=False
    ).generate_endpoints()

    api.GenericErtisApi(
        app,
        settings,
        endpoint_prefix='/api/v1/worksites',
        methods=['GET', 'POST', 'PUT', 'DELETE', 'QUERY'],
        resource_name='worksites',
        resource_service=ErtisGenericService,
        allow_to_anonymous=False
    ).generate_endpoints()

    api.GenericErtisApi(
        app,
        settings,
        endpoint_prefix='/api/v1/permission-groups',
        methods=['GET', 'POST', 'PUT', 'DELETE', 'QUERY'],
        resource_name='permission_groups',
        resource_service=ErtisGenericService,
        allow_to_anonymous=False
    ).generate_endpoints()
