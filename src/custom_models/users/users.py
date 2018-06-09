from passlib import hash


def hash_pwd(resource):

    hashed_password = hash.bcrypt.hash(resource["password"])
    resource["password"] = hashed_password

    return resource


def delete_critical_fields(resource):
    resource.pop('password', None)
    return resource


async def hash_updated_password(resource):
    if resource.get('password', None):
        hashed_password = hash.bcrypt.hash(resource['password'])
        resource['password'] = hashed_password

    return resource


def pipeline_functions():
    before_create = [hash_pwd]
    after_create = [delete_critical_fields]
    before_update = [hash_updated_password]
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
