# -*- coding: utf-8 -*-


import json

from tornado.web import RequestHandler, HTTPError
from tornado.escape import json_decode, utf8

from common.utils import ApiJSONEncoder


class BaseHandler(RequestHandler):
    COOKIE_KEYS = dict(
        SESSION_KEY='csk',  # coconut session key
    )
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.response = dict()

    def write_json(self):
        output = json.dumps(self.response, cls=ApiJSONEncoder)
        self.write(output)

    def write_error(self, status_code, **kwargs):
        self.set_status(status_code)
        self.response['message'] = '%d: %s' % (status_code, getattr(kwargs['exc_info'][1], 'log_message'))
        self.write_json()
    

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

    def set_default_headers(self):
        super().set_default_headers()
        self.set_header('Content-Type', 'application/json')
