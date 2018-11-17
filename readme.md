# Ertis Rest API
Register a rest API for 5 minutes. 

### Generic API Register and setup

Open the `src/rest.py` and register your api inside of `register_api()` function like below:

```python
def register_api(app, settings):
    
    app.users_api = api.GenericErtisApi(
        app,
        settings,
        endpoint_prefix='/api/v1/users',
        methods=['GET', 'POST', 'PUT', 'DELETE', 'QUERY'],
        resource_name='users',
        resource_service=ErtisGenericService,
        allow_anonymous=True
    )

```
- `app`: The current Flask App (current_app from register_api arg)
- `settings`: Current App settings from the used config (config from register_api arg)
- `endpoint_prefix`: Endpoint Prefix for registered api endpoint (string must be unique and startswith '/')
- `methods`: Define the allowed methods for registered api endpoint (Must be a string array and items must be HTTP methods)
- `resource_name`: This parameter must be unique. Used for resource name. (For mongodb collection name etc.)
- `ressource_service`: Write your resource service. You can use the default generic service ErtisGenericService If you don't have any service
- `allow_anonymous`: You can set True or False for the api endpoint authorization requirement (Must be boolean)


Then setup the registered api like below on same rest.py file.

```python
def setup_api(app):
    app.users_api.generate_endpoints(
        create_validation_schema=users_schema.CREATE_USER_SCHEMA,
        update_validation_schema=users_schema.UPDATE_USER_SCHEMA,
        before_create=[
            users.hash_pwd,
            users.ensure_email_is_unique,
            users.validate_permission_group_in_user
        ],
        after_create=[],
        before_update=[
            users.hash_updated_password,
            users.ensure_email_is_unique,
            users.validate_permission_group_in_user,
        ],
        after_update=[],
        before_delete=[],
        after_delete=[],
        read_formatter=[users.delete_critical_fields],
    )
```
- `create_validation_schema`: Create your validation schema in `resources` folder and use for api endpoint create validation.
If `POST` method not allowed for registered api endpoint you don't have to define this parameter
- `update_validation_schema`: Create your validation schema like create schema in `resources` folder and use for this endpoint update validation.
If `PUT` method not allowed for registered api endpoint you don't have to define this parameter 
- `before_create`: Use custom functions defined under the `resources` folder for before create pipeline. 
If `POST` method not allowed for registered api endpoint you don't have to define this parameter 
- `after_create`: Use custom functions defined under the `resources` folder for after create pipeline. 
If `POST` method not allowed for registered api endpoint you don't have to define this parameter
- `before_update`: Use custom functions defined under the `resources` folder for before update pipeline. 
If `PUT` method not allowed for registered api endpoint you don't have to define this parameter
- `after_update`: Use custom functions defined under the `resources` folder for after update pipeline. 
If `PUT` method not allowed for registered api endpoint you don't have to define this parameter
- `before_delete`: Use custom functions defined under the `resources` folder for before delete pipeline. 
If `DELETE` method not allowed for registered api endpoint you don't have to define this parameter
- `after_delete`: Use custom functions defined under the `resources` folder for after delete pipeline. 
If `DELETE` method not allowed for registered api endpoint you don't have to define this parameter
- `read_formatter`: Use custom functions defined under the `resources` folder for before response manipulation.

### Custom API Register and setup

Open the `src/custom_api` folder and create your api file line `users.py`. And create your api like below:

```python
def init_api(app, settings):
    @app.route('/api/path', methods=['POST'])
    def custom_api():
        pass
```

Note: `init_api(app, settings)` is required for the custom api registering. 

Add your custom api definition to `src/services.py` file like as below:

```python
def init_services(app, settings):
    app.generic_service = ErtisGenericRepository(app.db)

    from src.custom_api.users import init_api
    init_api(app, settings)

``` 

run your code. 



# Ertis Rest API Client Usage

Build your api quickly. Python language and flask framework was used to write Ertis Generic API. MongoDB the NoSQL database has been chosen. 

Author: ismetacar

## Tokens API

There are api's that can be used for registred users and anonymous users. Token api is implemented for anonymous users to use.

#### Usage

Request:
```python
Endpoint: /api/v1/tokens
Method: POST
Body:
{
    'email': 'email@email.com',
    'password': 'password'
}
```
Response:

```python
{
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJwcm4iOiI1YjFjMDUwMWRkNTUzMTEzMTUxZGI0MzMiLCJleHAiOjE1Mjg1Njk1NzksImp0aSI6IjViMWMxYjY3ZGQ1NTMxMTk0OTlmMTUxYiIsImlhdCI6MTUyODU2ODY3OX0.Edg8gTxDmMOC3E5IvPfH3QDzebNlmbzKvAsVO8d4UMY"
}
```

And the token in the response is used to access the other APIs.

## Refresh API
This api refresh to provided valid token.

#### Usage
Request:
```python
Endpoint: /api/v1/tokens/refresh
Method: POST
Body:
{
    'token': 'ey0...'
}
```

Response:
```python
{
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJwcm4iOiI1YjFjMDUwMWRkNTUzMTEzMTUxZGI0MzMiLCJleHAiOjE1Mjg1Njk1NzksImp0aSI6IjViMWMxYjY3ZGQ1NTMxMTk0OTlmMTUxYiIsImlhdCI6MTUyODU2ODY3OX0.Edg8gTxDmMOC3E5IvPfH3QDzebNlmbzKvAsVO8d4UMY"
}
```


## Me API
This Api prepare and return the aggregated informations of user that owner the token.

#### Usage

Request:
```python
Endpoint: /api/v1/me
Method: GET
Headers: 
{
    'Authorization': 'Bearer [token]'
}
```

Response:
```python
{
    "_id": "5b1c0501dd553113151db433",
    "email": "email@email.com",
    "username": "username",
    "fullname": "User Full Name",
    "permission_group": "permission-group",
    "permissions": [
        "ertis.materials.*",
        "ertis.worksites.*",
        "ertis.users.*"
    ]
}
```

## Generic APIs - (users, positions, projects, worksites, materials, material-types etc.)

These APIs are closed to the access of anonymous users. Need to get token from `tokens` api to use these APIs.

#### Usage
##### Creating a user:
Request:
```python
Endpoint: /api/v1/users
Method: POST
Headers:
{
    'Authorization': 'Bearer [token]'
}
Body:
{
    'username': 'username',
    'password': 'password',
    'fullname': 'fullname',
    'email': 'email@email.com'
}
```

Response: 
```python
{
    'username': 'username',
    'fullname': 'fullname',
    'email': 'email@email.com',
    '_id': '5b1c28d1dd55311d24403776'
}
```

The use of other APIs is the same as the use of Users Api.
