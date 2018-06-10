from passlib import hash

from src.utils.errors import ErtisError


def ensure_email_is_unique(resource, generic_service):
    email = resource.get('email', None)

    if not email:
        return resource

    users = generic_service.find_one_by(
        where={
            'email': email
        },
        collection='users',
        raise_exec=False
    )

    if users:
        raise ErtisError(
            err_code="errors.emailAddressIsUsedByAnotherUser",
            err_msg="The email address is being used by another user",
            status_code=400
        )

    return resource


def hash_pwd(resource, generic_service):

    hashed_password = hash.bcrypt.hash(resource["password"])
    resource["password"] = hashed_password

    return resource


def delete_critical_fields(resource, generic_service):
    resource.pop('password', None)
    return resource


def hash_updated_password(resource, generic_service):
    if resource.get('password', None):
        hashed_password = hash.bcrypt.hash(resource['password'])
        resource['password'] = hashed_password

    return resource


def validate_permission_group_in_user(resource, generic_service):
    provided_permission_group = resource.get('permission_group', None)
    if not provided_permission_group:
        return resource

    permission_group = generic_service.find_one_by(
        where={
            'slug': provided_permission_group
        },
        collection='permission_groups',
        raise_exec=False
    )

    if not permission_group:
        raise ErtisError(
            err_code="errors.permissionGroupNotFound",
            err_msg="Permission group not found, bad request received",
            status_code=400,
            context={
                'provided_permission_group': provided_permission_group
            }
        )

    return resource


def pipeline_functions():
    before_create = [
        hash_pwd,
        ensure_email_is_unique,
        validate_permission_group_in_user
    ]
    after_create = [delete_critical_fields]
    before_update = [
        hash_updated_password,
        ensure_email_is_unique,
        validate_permission_group_in_user,
    ]
    after_update = [delete_critical_fields]
    before_delete = []
    after_delete = []

    return {
        'before_create': before_create,
        'after_create': after_create,
        'before_update': before_update,
        'after_update': after_update,
        'before_delete': before_delete,
        'after_delete': after_delete
    }
