local_config = {
    "environment": "local",
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
        "active": True,
        "connection_string": "https://2a589cc99f0c43678dfa69386a52a397@sentry.io/1325189"
    },
    "email": {
        "active": True,
        "mail_server": "smtp.googlemail.com",
        "mail_port": 465,
        "mail_username": "ertis.f5@gmail.com",
        "mail_password": "****",
        "mail_use_tls": False,
        "mail_use_ssl": True
    }
}
