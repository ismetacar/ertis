CREATE_USER_SCHEMA = {
    '$schema': 'http://json-schema.org/schema#',
    'type': 'object',
    'properties': {
        'username': {
            'type': 'string',
            'minLength': 4
        },
        'fullname': {
            'type': 'string',
            'minLength': 4
        },
        'email': {
            'type': 'string',
        },
        'password': {
            'type': 'string',
            'minLength': 4
        },
        'permission_group': {
            'type': 'string'
        }
    },
    'required': [
        'username',
        'fullname',
        'email',
        'password',
        'permission_group'
    ]
}

UPDATE_USER_SCHEMA = {

}
