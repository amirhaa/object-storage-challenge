# Object Storage

## Description:

The project is a technical challange for [Arvan Cloud](arvancloud.com) and is written with technologies such as python, mongo, nginx, lua, docker and so on.

### Requirements to run

In order to run the project you need to have at least **docker** and **docker-compose** installed and also for development it is needed to have **python**, **python-virtualenv**, **python-pip** and so on.


### How to run:

First be sure to put appropriate environment varialbes in the env folder inside `.env` files. **should replace `.example.env` to `.env` files.

### For prodcution:

clone the project, then inside the root of the project
run ```./cmd build``` then ```./cmd prod```.

`./cmd build` would build following modules:
**middleware**, **webserver**.

`./cmd prod` would internally run `docker-compose up -d -f docker-compose.yml -f docker-compose.prod.yml`.

### For development:

clone the project, then inside the root of the project run
```./cmd build``` then ```./cmd dev```

## Modules:

### webserver module:

This module is **nginx** with **lua** and does the following:

1. Create `JWT Token` for the user
2. Validate `JWT Token` for each request
3. Proxy other request after **token validation** to **middleware** module

### middleware module:

This module is a `Flask` application with `Celery` and does the following:

1. For creating **buckets** check the prefix of the buckets to prevent the creation of repitive bucket name prefixes.
2. To upload files from client into [Arvan Cloud Object Storage](https://npanel.arvancloud.com/storage/) and use `Celery` and `boto3` library to achieve this matter.
