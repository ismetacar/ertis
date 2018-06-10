CREATE_TOKEN_SCHEMA = {
    '$schema': 'http://json-schema.org/schema#',
    'type': 'object',
    'properties': {
        'email': {
            'type': 'string'
        },
        'password': {
            'type': 'string'
        }
    },
    'required': [
        'email',
        'password'
    ]
}
