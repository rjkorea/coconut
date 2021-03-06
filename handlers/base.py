# -*- coding: utf-8 -*-


import json
from bson import ObjectId
from ast import literal_eval
import jwt

from tornado.web import RequestHandler, HTTPError
from tornado.websocket import WebSocketHandler
from tornado.escape import json_decode, utf8, url_unescape

from common.utils import ApiJSONEncoder

from models.admin import AdminModel
from models.session import AdminSessionModel, UserSessionModel
from models.user import UserModel


class BaseHandler(RequestHandler):
    COOKIE_KEYS = dict(
        SESSION_KEY='csk',  # coconut session key for admin
        USER_SESSION_KEY='usk',  # coconut session key for user
        MOBILE_APP_KEY='mak', # for mobile app
        TABLET_APP_KEY='tak' # for tablet app
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
                            'Content-Type, X-Requested-With, _xsrf, X-XSRFToken, Accept-Encoding, Authorization, Set-Cookie')
            self.set_header('Access-Control-Allow-Credentials', 'true')
            self.set_header('Access-Control-Max-Age', 1800)

    def set_error(self, code, message):
        return repr(dict(code=code, message=message))

    def write_json(self):
        output = json.dumps(self.response, cls=ApiJSONEncoder)
        self.write(output)

    def write_error(self, status_code, **kwargs):
        self.set_status(status_code)
        error = getattr(kwargs['exc_info'][1], 'log_message')
        if error.startswith('{'):
            self.response['error'] = literal_eval(getattr(kwargs['exc_info'][1], 'log_message'))
        else:
            self.response['message'] = '%d: %s' % (status_code, getattr(kwargs['exc_info'][1], 'log_message'))
        self.write_json()

    def get_authorization(self):
        return self.request.headers.get('Authorization')

    def get_authorization_access_token(self):
        auth = self.request.headers.get('Authorization', None)
        if auth:
            return auth.strip().split(' ')[1]
        return auth

    def get_authorization_usk(self):
        auth = self.request.headers.get('Authorization', None)
        if auth:
            return auth.strip().split('=')[1]
        return auth

    def get_authorization_csk(self):
        auth = self.request.headers.get('Authorization', None)
        if auth:
            return auth.strip().split('=')[1]
        return auth

    async def get_current_admin_async(self):
        current_user = None
        session_key = self.get_authorization_csk()
        if not session_key:
            return None
        session = await AdminSessionModel.find_one({'_id': ObjectId(session_key)})
        if not session:
            return None
        return  await AdminModel.find_one({'_id': session['admin_oid']})

    async def get_current_user_async(self):
        current_user = None
        session_key = self.get_authorization_usk()
        if not session_key:
            return None
        session = await UserSessionModel.find_one({'_id': ObjectId(session_key)})
        if not session:
            return None
        return  await UserModel.find_one({'_id': session['user_oid']})

    async def get_current_user_access_token_async(self):
        current_user = None
        access_token = self.get_authorization_access_token()
        if not access_token:
            return None
        try:
            decoded_jwt = jwt.decode(access_token, 'tkitcoconut', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise HTTPError(401, 'access token expired')
        return  await UserModel.find_one({'_id': ObjectId(decoded_jwt['user_oid'])})

    async def get_current_app_async(self):
        mobile_app_key = self.get_cookie(self.COOKIE_KEYS['MOBILE_APP_KEY'], None)
        if not mobile_app_key:
            return None
        return  mobile_app_key

    async def get_current_tablet_async(self):
        tablet_code = self.get_cookie(self.COOKIE_KEYS['TABLET_APP_KEY'], None)
        if not tablet_code:
            return None
        return  await AdminModel.find_one({'tablet_code': tablet_code})


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


class MultipartFormdataHandler(BaseHandler):
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.json_decoded_body = dict()

    def prepare(self):
        super(MultipartFormdataHandler, self).prepare()

        if self.request.body_arguments:
            try:
                for k, v in self.request.body_arguments.items():
                    self.json_decoded_body[k] = url_unescape(v[0])
            except ValueError:
                raise HTTPError(400, 'Unable parse to JSON.')
        else:
            self.json_decoded_body = dict()

    def set_default_headers(self):
        super().set_default_headers()
        self.set_header('Content-Type', 'application/json')


class WSHandler(WebSocketHandler):
    clients = list()
    def open(self):
        WSHandler.clients.append(self)

    def on_close(self):
        WSHandler.clients.remove(self)

    def check_origin(self, origin):
        return True

    @classmethod
    def write_to_clients(cls, data):
        if cls.clients:
            for client in cls.clients:
                client.write_message(data)
