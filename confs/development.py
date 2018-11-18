development_config = {
    "environment": "development",
    "mongo_connection_string": "mongodb://localhost:27017/ertis",
    "api_version": "v1",
    "application_secret": "AtqVaL11EHVPEpbu2mr0yZgKXj1BnRj0",
    "token_ttl": 60,
    "default_database": "ertis",
    "verify_token": False,
    "error_handler": True,
    "debug": True,
    "port": 8888,
    "sentry": {
        "active": False,
        "connection_string": ""
    },
    "email": {
        "active": False,
        "mail_server": "",
        "mail_port": 465,
        "mail_username": "",
        "mail_password": "",
        "mail_use_tls": False,
        "mail_use_ssl": True
    }
}
