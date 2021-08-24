import os
import tempfile

import unittest
import pytest

from flask import Flask
from flask_mongoengine import MongoEngine
from mongoengine import connect
from mongoengine.connection import disconnect
from models import User, Prefix, UserPrefix
from views import bucket_api_blueprint, bucket_api_v2_blueprint

user1 = {
    'username': 'john',
    'password': '1234',
}

user2 = {
    'username': 'sarah',
    'password': '4321'
}


class TestBucketApi(unittest.TestCase):
    api_blueprint = bucket_api_blueprint
    path = '/bucket'
    
    client = None
    db = None

    @classmethod
    def setUpClass(cls):
        # create a new flask app to use in test
        app = Flask(__name__)
        app.config.from_object('config.TestConfig')
        app.register_blueprint(cls.api_blueprint)

        # set the client test
        cls.client = app.test_client()

        # create mongo connection
        cls.db = MongoEngine(app)

        # clear database if it has already any data
        User.drop_collection()
        Prefix.drop_collection()
        UserPrefix.drop_collection()

        # load our fixtures into mongo
        cls.init_data()

    @classmethod
    def tearDownClass(cls):
        # clear database fixtures
        User.drop_collection()
        Prefix.drop_collection()
        UserPrefix.drop_collection()

        cls.db.disconnect()
        
    @classmethod
    def init_data(cls):
        cls.u1 = User(**user1).save()
        cls.u2 = User(**user2).save()

        cls.p1 = Prefix(prefix='arv').save()
        cls.p2 = Prefix(prefix='cloud').save()
        cls.p3 = Prefix(prefix='arvan').save()
        cls.p4 = Prefix(prefix='bucket').save()
        
        cls.up1 = UserPrefix(user_id=cls.u1, prefix_id=cls.p1, is_allowed=True).save()
        cls.up2 = UserPrefix(user_id=cls.u1, prefix_id=cls.p2, is_allowed=False).save()
        cls.up3 = UserPrefix(user_id=cls.u1, prefix_id=cls.p3, is_allowed=True).save()
        cls.up4 = UserPrefix(user_id=cls.u2, prefix_id=cls.p1, is_allowed=False).save()
        cls.up5 = UserPrefix(user_id=cls.u2, prefix_id=cls.p2, is_allowed=False).save()
        cls.up6 = UserPrefix(user_id=cls.u2, prefix_id=cls.p3, is_allowed=False).save()
        
    def test_payload_is_empty(self):
        result = self.client.post(self.path, json={})

        self.assertEqual(result.status_code, 400)

    def test_payload_bucket_name_should_be_min_three_characters(self):
        result = self.client.post(self.path, json={'bucket': 'ab'})

        self.assertEqual(result.json['bucket'], ['Shorter than minimum length 3.'])
        self.assertEqual(result.status_code, 400)

    def test_payload_for_required_fields(self):
        result = self.client.post(self.path, json={'bucket': 'bucket'})
        
        self.assertEqual(result.json['username'], ['Missing data for required field.'])
        self.assertEqual(result.status_code, 400)

    def test_bucket_that_is_false_allowed_for_user(self):
       # u1, p2, up2
       bucket = f'{self.p2.prefix}sth'
       result = self.client.post(self.path, json={'username': self.u1.username, 'bucket': bucket})
       
       self.assertEqual(result.json['error'], f"you are not allowed to use '{bucket}', please try something else")
       self.assertEqual(result.status_code, 400)

    def test_unavailable_bucket_that_is_already_in_prefix_model(self):
        # u1, p4
        bucket = f'{self.p4.prefix}sht'
        result = self.client.post(self.path, json={'username': self.u1.username, 'bucket': bucket})
        
        self.assertEqual(result.json['error'], f"cannot use '{bucket}', it is already taken, please try something else")
        self.assertEqual(result.status_code, 400)

    def test_bucket_name_that_is_totally_available_to_use(self):
        # u2
        bucket = "randombucketname"
        result = self.client.post(self.path, json={'username': self.u2.username, 'bucket': bucket})

        self.assertEqual(result.status_code, 200)


class TestBucketApiV2(TestBucketApi):
    api_blueprint = bucket_api_v2_blueprint
    path = 'bucket-v2'
