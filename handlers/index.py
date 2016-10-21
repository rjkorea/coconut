# -*- coding: utf-8 -*-

from datetime import datetime
from bson import ObjectId

from tornado.web import HTTPError

from handlers.base import JsonHandler
from models.test import TestModel


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
