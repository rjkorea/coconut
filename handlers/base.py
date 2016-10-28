# -*- coding: utf-8 -*-


import json
from bson import ObjectId

from tornado.web import RequestHandler, HTTPError
from tornado.escape import json_decode, utf8

from common.utils import ApiJSONEncoder

from models.admin import AdminModel
from models.session import AdminSessionModel


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
    
    async def get_current_admin_async(self):
        current_user = None
        session_key = self.get_cookie(self.COOKIE_KEYS['SESSION_KEY'], None)
        if not session_key:
            return None
        session = await AdminSessionModel.find_one({'_id': ObjectId(session_key)})
        if not session:
            return None
        return  await AdminModel.find_one({'_id': session['admin_oid']})


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
