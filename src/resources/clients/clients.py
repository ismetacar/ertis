import datetime

CREATE_CLIENT_SCHEMA = {
    '$schema': 'http://json-schema.org/schema#',
    'type': 'object',
    'properties': {
        '_id': {
            'type': 'string',
            'minLength': 4
        },
        'name': {
            'type': 'string',
            'minLength': 4
        },
        'domain': {
            'type': 'string',
            'minLength': 4
        }
    },
    'required': [
        '_id',
        'name',
        'domain'
    ]
}


def create_project(client_id, db):
    project = {
        "name": client_id,
        "image": {},
        "domain": "",
        "client_id": client_id,
        "_sys": {
            "created_by": "system",
            "created_at": datetime.datetime.utcnow(),
            "collection": "projects"
        }
    }

    return db.projects.save(project)


PERMISSION_GROUPS = {
        'admin': ['ertis.*'],
        'manager': ['ertis.*'],
        'staff': ['ertis.*']
    }


def create_default_permission_groups(client_id, db):

    created_permission_groups = []
    for permission_group in PERMISSION_GROUPS.keys():
            data = {
                'slug': permission_group,
                'name': permission_group,
                'is_default': True,
                'client_id': client_id,
                'permissions': PERMISSION_GROUPS[permission_group],
                'sys': {
                    'created_at': datetime.datetime.utcnow(),
                    'created_by': 'system',
                    'collection': 'permission_groups'
                }
            }

            created_permission_groups.append(db.permission_groups.save(data))

    return created_permission_groups
