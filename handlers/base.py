# -*- coding: utf-8 -*-


import json

from tornado.web import RequestHandler, HTTPError
from tornado.escape import json_decode, utf8


class BaseHandler(RequestHandler):
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.response = dict()

    def write_json(self):
        self.write(self.response)


class JsonHandler(BaseHandler):
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.json_decoded_body = dict()

    def prepare(self):
        super(JsonHandler, self).prepare()

        if self.request.body:
            try:
                self.json_decoded_body = json_decode(utf8(self.request.body))
            except ValueError:
                raise HTTPError(400, 'Unable parse to JSON.')
        else:
            self.json_decoded_body = dict()
