# -*- coding: utf-8 -*-

from datetime import datetime
from bson import ObjectId

from tornado.web import HTTPError

from handlers.base import JsonHandler
from models.user import UserModel
from models.session import UserSessionModel

from common.decorators import parse_argument
from common import hashers


class DuplicatedHandler(JsonHandler):
    @parse_argument([('email', str, None), ('mobile_number', str, None)])
    async def get(self, *args, **kwargs):
        parsed_args = kwargs.get('parsed_args')
        if not parsed_args['email'] and not parsed_args['mobile_number']:
            raise HTTPError(400, 'no params (email or mobile_number)')
        if parsed_args['email']:
            user = await UserModel.find_one({'email': parsed_args['email'], 'enabled': True})
            if user:
                self.response['data'] = 'OK'
            else:
                raise HTTPError(400, 'no exist email')
        elif parsed_args['mobile_number']:
            user = await UserModel.find_one({'mobile_number': parsed_args['mobile_number'], 'enabled': True})
            if user:
                self.response['data'] = 'OK'
            else:
                raise HTTPError(400, 'no exist mobile number')
        else:
            self.response['data'] = None
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class LoginHandler(JsonHandler):
    async def put(self, *args, **kwargs):
        type = self.json_decoded_body.get('type', None)
        if not type:
            raise HTTPError(400, 'type param is required(email, kakao, facebook, google, naver)')
        if type == 'email':
            email = self.json_decoded_body.get('email', None)
            if not email:
                raise HTTPError(400, 'invalid email')
            password = self.json_decoded_body.get('password', None)
            if not password:
                raise HTTPError(400, 'invalid password')
            user = await UserModel.find_one({'email': email, 'enabled': True})
            if not user:
                raise HTTPError(400, 'no exist email')
            if not hashers.check_password(password, user['password']):
                raise HTTPError(400, 'invalid password')
        else:
            raise HTTPError(400, 'invalid type(email, kakao, facebook, google, naver)')
        session = UserSessionModel()
        session.data['user_oid'] = user['_id']
        session_oid = await session.insert()
        self.response['data'] = {
            'usk': str(session_oid)
        }
        self.write_json()

    async def option(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()
