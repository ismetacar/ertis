from src.generics import api
from src.generics.service import ErtisGenericService
from src.resources.permission_groups import permission_groups, permission_groups_schema
from src.resources.users import users, users_schema


def register_api(app, settings):
    api.GenericErtisApi(
        app,
        settings,
        endpoint_prefix='/api/v1/users',
        methods=['GET', 'POST', 'PUT', 'DELETE', 'QUERY'],
        resource_name='users',
        resource_service=ErtisGenericService,
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
        after_delete=[]
    ).generate_endpoints()

    api.GenericErtisApi(
        app,
        settings,
        endpoint_prefix='/api/v1/permission-groups',
        methods=['GET', 'POST', 'PUT', 'DELETE', 'QUERY'],
        resource_name='permission_groups',
        resource_service=ErtisGenericService,
        create_validation_schema=permission_groups_schema.CREATE_PERMISSION_GROUP_SCHEMA,
        update_validation_schema=permission_groups_schema.UPDATE_PERMISSION_GROUP_SCHEMA,
        before_create=[
            permission_groups.generate_permission_group_slug,
            permission_groups.check_slug_conflict
        ],
        after_create=[],
        before_update=[
            permission_groups.disallow_predefined_permission_group_operations,
            permission_groups.check_slug_conflict
        ],
        after_update=[],
        before_delete=[
            permission_groups.disallow_predefined_permission_group_operations
        ],
        after_delete=[]
    ).generate_endpoints()

    api.GenericErtisApi(
        app,
        settings,
        endpoint_prefix='/api/v1/permission-groups',
        methods=['GET', 'POST', 'PUT', 'DELETE', 'QUERY'],
        resource_name='permission_groups',
        resource_service=ErtisGenericService,
        create_validation_schema=permission_groups_schema.CREATE_PERMISSION_GROUP_SCHEMA,
        update_validation_schema=permission_groups_schema.UPDATE_PERMISSION_GROUP_SCHEMA,
        before_create=[
            permission_groups.generate_permission_group_slug,
            permission_groups.check_slug_conflict
        ],
        after_create=[],
        before_update=[
            permission_groups.disallow_predefined_permission_group_operations,
            permission_groups.check_slug_conflict
        ],
        after_update=[],
        before_delete=[
            permission_groups.disallow_predefined_permission_group_operations
        ],
        after_delete=[]
    ).generate_endpoints()
