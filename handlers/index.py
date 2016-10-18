# -*- coding: utf-8 -*-

from datetime import datetime
from bson import ObjectId

from handlers.base import JsonHandler


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
        self.response['data'] = 'test handler'
        self.write_json()

    async def put(self, *args, **kwargs):
        self.response['data'] = self.json_decoded_body
        self.response['created_at'] = datetime.now()
        self.response['_id'] = ObjectId()
        self.write_json()


