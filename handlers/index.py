# -*- coding: utf-8 -*-

from tornado.web import RequestHandler


class PingHandler(RequestHandler):
    async def get(self):
        return 'ping...'
