# -*- coding: utf-8 -*-

from handlers.base import JsonHandler


class IndexHandler(JsonHandler):
    async def get(self, *args, **kwargs):
        self.response['data'] = 'index handler'
        return self.write_json()

    async def put(self, *args, **kwargs):
        self.response['data'] = self.json_decoded_body
        return self.write_json()


class PingHandler(JsonHandler):
    async def get(self, *args, **kwargs):
        self.response['data'] = 'ping handler'
        return self.write_json()

    async def put(self, *args, **kwargs):
        self.response['data'] = self.json_decoded_body
        return self.write_json()
