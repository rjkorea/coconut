# -*- coding: utf-8 -*-

from datetime import datetime
from bson import ObjectId

from handlers.base import JsonHandler
from services.mongodb import MongodbService


class IndexHandler(JsonHandler):
    async def get(self, *args, **kwargs):
        self.response['data'] = 'index handler'
        self.write_json()

    async def put(self, *args, **kwargs):
        self.response['data'] = self.json_decoded_body
        self.response['created_at'] = datetime.now()
        self.response['_id'] = ObjectId()
        self.write_json()


class PingHandler(JsonHandler):
    async def get(self, *args, **kwargs):
        self.response['data'] = 'ping handler'
        self.write_json()

    async def put(self, *args, **kwargs):
        self.response['data'] = 'ping handler'
        self.write_json()

    async def delete(self, *args, **kwargs):
        self.response['data'] = 'ping handler'
        self.write_json()

    async def post(self, *args, **kwargs):
        self.response['data'] = 'ping handler'
        self.write_json()


class TestHandler(JsonHandler):
    async def get(self, *args, **kwargs):
        res = await MongodbService().client['test'].find_one()
        self.response['data'] = res
        self.write_json()

    async def put(self, *args, **kwargs):
        data = self.json_decoded_body
        data['created_at'] = datetime.utcnow()
        res = await MongodbService().client['test'].insert(data)
        self.response['data'] = dict(
            _id=str(res)
        )
        self.write_json()
