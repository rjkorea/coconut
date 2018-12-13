# -*- coding: utf-8 -*-

from datetime import datetime
from bson import ObjectId

from tornado.web import HTTPError

from handlers.base import JsonHandler
from models.user import UserModel, UserAutologinModel
from models.session import UserSessionModel

from models import send_sms

from common.decorators import parse_argument
from common import hashers

import settings


class RegisterHandler(JsonHandler):
    async def post(self, *args, **kwargs):
        mobile_number = self.json_decoded_body.get('mobile_number', None)
        if not mobile_number or len(mobile_number) == 0:
            raise HTTPError(400, 'invalid mobile_number')
        duplicated_user = await UserModel.find_one({'mobile_number': mobile_number, 'enabled': True})
        if duplicated_user:
            raise HTTPError(400, 'exist mobile number')
        email = self.json_decoded_body.get('email', None)
        if not email or len(email) == 0:
            raise HTTPError(400, 'invalid email')
        name = self.json_decoded_body.get('name', None)
        if not name or len(name) == 0:
            raise HTTPError(400, 'invalid name')
        last_name = self.json_decoded_body.get('last_name', None)
        if not last_name or len(last_name) == 0:
            raise HTTPError(400, 'invalid last_name')
        birthday = self.json_decoded_body.get('birthday', None)
        if not birthday or len(birthday) != 8 :
            raise HTTPError(400, 'invalid birthday(YYYYMMDD)')
        gender = self.json_decoded_body.get('gender', None)
        if not gender or (gender != 'male' and gender != 'female' and gender != 'not_specific'):
            raise HTTPError(400, 'invalid gender(male, female, not_specific)')
        password = self.json_decoded_body.get('password', None)
        if not password or len(password) == 0 or not hashers.validate_user_password_v2(password):
            raise HTTPError(400, 'invalid password')
        user = UserModel(raw_data=dict(
            mobile_number=mobile_number,
            email=email,
            name=name,
            last_name=last_name,
            birthday=birthday,
            gender=gender,
            terms={'privacy': True, 'policy': True}
        ))
        sns = self.json_decoded_body.get('sns', None)
        if sns:
            if 'type' not in sns or 'id' not in sns:
                raise HTTPError(400, 'invalid sns(type and id)')
            user.data['sns'] = sns
        user.set_password(password)
        await user.insert()
        self.response['data'] = 'OK'
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


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
    async def post(self, *args, **kwargs):
        type = self.json_decoded_body.get('type', None)
        if not type:
            raise HTTPError(400, 'type param is required(mobile_number)')
        if type == 'mobile_number':
            mobile_number = self.json_decoded_body.get('mobile_number', None)
            if not mobile_number:
                raise HTTPError(400, 'invalid mobile_number')
            password = self.json_decoded_body.get('password', None)
            if not password or len(password) < 4:
                raise HTTPError(400, 'invalid password')
            user = await UserModel.find_one({'mobile_number': mobile_number, 'enabled': True})
            if not user:
                raise HTTPError(400, 'no exist mobile_number')
            if not hashers.check_password(password, user['password']):
                raise HTTPError(400, 'wrong password')
        else:
            raise HTTPError(400, 'invalid type(mobile_number)')
        session = UserSessionModel()
        session.data['user_oid'] = user['_id']
        session_oid = await session.insert()
        self.response['data'] = {
            'usk': str(session_oid)
        }
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class UserHandler(JsonHandler):
    @parse_argument([('mobile_number', str, None)])
    async def get(self, *args, **kwargs):
        parsed_args = kwargs.get('parsed_args')
        if not parsed_args['mobile_number'] or len(parsed_args['mobile_number']) == 0:
            raise HTTPError(400, 'invalid mobile_number')
        q = {
            'mobile_number': parsed_args['mobile_number'],
            'enabled': True
        }
        user = await UserModel.find_one(query=q)
        if not user:
            raise HTTPError(400, 'no exist user')
        res = dict()
        if 'password' in user:
            res['has_password'] = True
        else:
            res['has_password'] = False
        self.response['data'] = res
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class AutoLoginHandler(JsonHandler):
    async def put(self, *args, **kwargs):
        mobile_number = self.json_decoded_body.get('mobile_number', None)
        if not mobile_number:
            raise HTTPError(400, 'invalid mobile_number')
        content_oid = self.json_decoded_body.get('content_oid', None)
        if not content_oid:
            raise HTTPError(400, 'invalid content_oid')
        user = await UserModel.find_one({'mobile_number': mobile_number, 'enabled': True})
        if not user:
            raise HTTPError(400, 'not exist user')
        session = UserSessionModel()
        session.data['user_oid'] = user['_id']
        session_oid = await session.insert()
        usk = str(session_oid)
        userautologin = UserAutologinModel()
        userautologin.data['usk'] = session_oid
        userautologin.data['content_oid'] = ObjectId(content_oid)
        userautologin_oid = await userautologin.insert()
        config = settings.settings()
        is_sent_receiver = await send_sms(
            {
                'type': 'unicode',
                'from': 'tkit',
                'to': mobile_number,
                'text': 'http://%s:%s/autologin/%s' % (config['web']['host'], config['web']['port'], userautologin_oid)
            }
        )
        self.response['message'] = 'check your sms'
        self.response['is_sent_receiver'] = is_sent_receiver
        self.write_json()


    async def get(self, *args, **kwargs):
        autologin_oid = kwargs.get('_id', None)
        if not autologin_oid or len(autologin_oid) != 24:
            raise HTTPError(400, 'invalid autologin_oid')
        result = await UserAutologinModel.find_one({'_id': ObjectId(autologin_oid)})
        if not result:
            raise HTTPError(400, 'not exist autologin session')
        self.response['data'] = result
        self.write_json()


    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()
