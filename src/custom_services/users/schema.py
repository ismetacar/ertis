CREATE_USER_SCHEMA = {
    '$schema': 'http://json-schema.org/schema#',
    'type': 'object',
    'properties': {
        'username': {
            'type': 'string'
        },
        'fullname': {
            'type': 'string'
        },
        'email': {
            'type': 'string'
        },
        'password': {
            'type': 'string'
        }
    },
    'required': [
        'username',
        'fullname',
        'email',
        'password'
    ]
}

UPDATE_USER_SCHEMA = {

}
