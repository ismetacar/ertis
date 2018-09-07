from slugify import slugify

from src.utils.errors import ErtisError


def generate_permission_group_slug(resource):
    name = resource.get('name')
    slug = slugify(name)
    resource['slug'] = slug

    return resource


def disallow_predefined_permission_group_operations(resource):
    if resource.get('is_default', None):
        raise ErtisError(
            err_msg="Predefined permission groups cant be deleted or changed",
            err_code="errors.predefinedPermissionGroupsCantBeChangedOrDeleted",
            status_code=403
        )

    return resource


def check_slug_conflict(resource, generic_service):
    slug = resource.get('slug')
    founded_permission_group = generic_service.find_one_by(
        where={
            'slug': slug
        },
        collection='permission_groups',
        raise_exec=False
    )

    if founded_permission_group:
        raise ErtisError(
            err_code="errors.permissionGroupAlreadyExists",
            err_msg="Permission group already exists with given slug: <{}>".format(slug),
            status_code=400
        )
