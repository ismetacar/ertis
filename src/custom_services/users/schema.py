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
