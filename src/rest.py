from src.generics import api
from src.generics.service import ErtisGenericService
from src.resources.users import users, users_schema


def register_api(app, settings):
    app.users_api = api.GenericErtisApi(
        app,
        settings,
        endpoint_prefix='/api/v1/users',
        methods=['GET', 'POST', 'PUT', 'DELETE', 'QUERY'],
        resource_name='users',
        resource_service=ErtisGenericService,
        allow_anonymous=True
    )


def setup_api(app):
    app.users_api.generate_endpoints(
        create_validation_schema=users_schema.CREATE_USER_SCHEMA,
        update_validation_schema=users_schema.UPDATE_USER_SCHEMA,
        before_create=[
            users.hash_pwd,
            users.ensure_email_is_unique,
            users.validate_permission_group_in_user
        ],
        after_create=[],
        before_update=[
            users.hash_updated_password,
            users.ensure_email_is_unique,
            users.validate_permission_group_in_user,
        ],
        after_update=[],
        before_delete=[],
        after_delete=[],
        read_formatter=[users.delete_critical_fields],
    )
