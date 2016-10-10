# -*- coding: utf-8 -*-

from tornado.web import RequestHandler


class IndexHandler(RequestHandler):
    async def get(self):
        return self.write('index handler')


class PingHandler(RequestHandler):
    async def get(self):
        return self.write('ping handler')
