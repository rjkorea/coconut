# -*- coding: utf-8 -*-

from datetime import datetime
from bson import ObjectId

from tornado.web import HTTPError

from handlers.base import JsonHandler
from models.test import TestModel
from models.admin import AdminModel

from common import hashers


class IndexHandler(JsonHandler):
    async def get(self, *args, **kwargs):
        self.response['data'] = 'index handler'
        self.write_json()


class PingHandler(JsonHandler):
    async def get(self, *args, **kwargs):
        self.response['data'] = 'ping GET handler'
        self.write_json()

    async def put(self, *args, **kwargs):
        self.response['data'] = 'ping PUT handler'
        self.write_json()

    async def delete(self, *args, **kwargs):
        self.response['data'] = 'ping DELETE handler'
        self.write_json()

    async def post(self, *args, **kwargs):
        self.response['data'] = 'ping POST handler'
        self.write_json()


class TestHandler(JsonHandler):
    async def get(self, *args, **kwargs):
        result = await TestModel.find()
        self.response['data'] = result 
        self.write_json()

    async def put(self, *args, **kwargs):
        oid = kwargs.get('oid', None)
        if oid is None:
            raise HTTPError(400, 'required \'oid\'')
        data = self.json_decoded_body
        query = {
            '_id': ObjectId(oid)
        }
        data['updated_at'] = datetime.utcnow()
        doc = {
            '$set': data
        }
        result = await TestModel.update(query, doc, False, False)
        self.response['data'] = result
        self.write_json()

    async def post(self, *args, **kwargs):
        data = self.json_decoded_body
        model = TestModel(raw_data=data)
        result = await model.insert()
        self.response['data'] = result
        self.write_json()


class AuthHandler(JsonHandler):
    async def get(self, *args, **kwargs):
        self.response['data'] = dict()
        self.write_json()

    async def put(self, *args, **kwargs):
        self.response['data'] = dict()
        self.write_json()

    async def post(self, *args, **kwargs):
        email = self.json_decoded_body.get('email', None)
        if not email or len(email) == 0:
            raise HTTPError(400, 'invalid email')
        name = self.json_decoded_body.get('name', None)
        if not name or len(name) == 0:
            raise HTTPError(400, 'invalid name')
        password = self.json_decoded_body.get('password', None)
        if not password or len(password) == 0 or not hashers.validate_password(password):
            raise HTTPError(400, 'invalid password')
        password2 = self.json_decoded_body.get('password2', None)
        if not password or len(password) == 0 or not hashers.validate_password(password):
            raise HTTPError(400, 'invalid password2')
        if password != password2:
            raise HTTPError(400, 'password and password2 not matched')
        duplicated_admin = await AdminModel.find_one({'email': email})
        if duplicated_admin:
            raise HTTPError(400, 'duplicated email')
        admin = AdminModel(raw_data=dict(
            email=email,
            name=name
        ))
        admin.set_password(password)
        result = await admin.insert()
        self.response['data'] = result
        self.write_json()
