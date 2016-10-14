# -*- coding: utf-8 -*-

from datetime import datetime

from handlers.base import JsonHandler


class IndexHandler(JsonHandler):
    async def get(self, *args, **kwargs):
        self.response['data'] = 'index handler'
        self.write_json()

    async def put(self, *args, **kwargs):
        self.response['data'] = self.json_decoded_body
        self.response['created_at'] = datetime.now()
        self.write_json()


class PingHandler(JsonHandler):
    async def get(self, *args, **kwargs):
        self.response['data'] = 'ping handler'
        self.write_json()

    async def put(self, *args, **kwargs):
        self.response['data'] = self.json_decoded_body
        self.write_json()
