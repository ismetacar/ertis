CREATE_PERMISSION_GROUP_SCHEMA = {
    '$schema': 'http://json-schema.org/schema#',
    'type': 'object',
    'properties': {
        'name': {
            'type': 'string',
            'minLength': 4
        },
        'permissions': {
            'type': 'array'
        }
    },
    'required': [
        'name',
        'permissions'
    ]
}

UPDATE_PERMISSION_GROUP_SCHEMA = CREATE_PERMISSION_GROUP_SCHEMA
