# Ertis Rest API

This api will use for warehouse management system. Python language and flask framework was used to write Ertis Generic API. MongoDB the NoSQL database has been chosen. 

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
