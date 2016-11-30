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
        MOBILE_APP_KEY='mak' # for mobile app
    )
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.response = dict()

    def set_default_headers(self):
        origin = self.request.headers.get('Origin')
        if origin:
            self.set_header('Access-Control-Allow-Origin', origin)
            self.set_header('Access-Control-Allow-Methods', 'GET, POST, PUT, PATCH, DELETE, OPTIONS')
            self.set_header('Access-Control-Allow-Headers',
                            'Content-Type, X-Requested-With, _xsrf, X-XSRFToken, Accept-Encoding, Authorization')
            self.set_header('Access-Control-Allow-Credentials', 'true')
            self.set_header('Access-Control-Max-Age', 1800)

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

    async def get_current_app_async(self):
        mobile_app_key = self.get_cookie(self.COOKIE_KEYS['MOBILE_APP_KEY'], None)
        if not mobile_app_key:
            return None
        return  mobile_app_key


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
