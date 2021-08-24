import logging
from flask import Flask
from config import IS_DEVELPMENT
from flask_mongoengine import MongoEngine
from make_celery import make_celery
from views import bucket_api_blueprint, upload_file_blueprint

# Create Flask app
app = Flask(__name__)

# Set logger level
app.logger.setLevel(logging.DEBUG)

# set initial env to flask app
app.config.from_object('config.DevelopmentConfig' if IS_DEVELPMENT else 'config.ProductionConfig')

# create a celery instance
celery = make_celery(app)

# initialize mongodb connection
MongoEngine(app)

# register blueprints
app.register_blueprint(bucket_api_blueprint)
app.register_blueprint(upload_file_blueprint)

if __name__ == "__main__":
    app.run()
