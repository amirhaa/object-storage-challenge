import os

IS_DEVELPMENT = os.environ.get("FLASK_ENV", "production") == 'development'


class Config(object):
    TESTING = False
    UPLOAD_FOLDER = 'uploads'
    MONGODB_SETTINGS = {
        'connect': False,
        'host': os.environ.get("MONGO_CONNECTION_STRING")
    }
    CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND")
    CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL")
    ARVAN_ACCESS_KEY = os.environ.get('ARVAN_ACCESS_KEY')
    ARVAN_SECRET_KEY = os.environ.get('ARVAN_SECRET_KEY')
    ARVAN_ENDPOINT_URL = os.environ.get('ARVAN_ENDPOINT_URL')


class ProductionConfig(Config):
    pass


class DevelopmentConfig(Config):
    pass


class TestConfig(Config):
    TESTING = True
    MONGODB_SETTINGS = {
        'connect': False,
        'host': os.environ.get("MONGO_TEST_CONNECTION_STRING")
    }
