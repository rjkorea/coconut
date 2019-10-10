# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from bson import ObjectId

from tornado.web import HTTPError

from handlers.base import JsonHandler
from models.user import UserModel, UserAutologinModel
from models.session import UserSessionModel
from models.sms_verification import SmsVerificationModel

from models import send_sms

from models import create_user_v2

from common.decorators import parse_argument
from common import hashers

from services.lms import LmsService
from services.sms import NexmoService

import logging
import settings


class RegisterHandler(JsonHandler):
    async def post(self, *args, **kwargs):
        mobile_country_code = self.json_decoded_body.get('mobile_country_code', None)
        if not mobile_country_code:
            raise HTTPError(400, 'invalid mobile_country_code')
        mobile_number = self.json_decoded_body.get('mobile_number', None)
        if not mobile_number or len(mobile_number) < 9 :
            raise HTTPError(400, 'invalid mobile_number')
        duplicated_user = await UserModel.find_one({'mobile.country_code': mobile_country_code, 'mobile.number': mobile_number, 'enabled': True})
        if duplicated_user and 'password' in duplicated_user:
            raise HTTPError(400, 'exist mobile number')
        name = self.json_decoded_body.get('name', None)
        if not name or len(name.strip()) == 0:
            raise HTTPError(400, 'invalid name')
        birthday = self.json_decoded_body.get('birthday', None)
        if not birthday or len(birthday) != 4 :
            raise HTTPError(400, 'invalid birthday(YYYY)')
        gender = self.json_decoded_body.get('gender', None)
        if not gender or gender not in UserModel.GENDER:
            raise HTTPError(400, 'invalid gender(male, female, others)')
        password = self.json_decoded_body.get('password', None)
        if not password or len(password) == 0 or not hashers.validate_user_password_v2(password):
            raise HTTPError(400, 'invalid password')

        if duplicated_user and 'password' not in duplicated_user:
            doc = dict(
                mobile=dict(
                    country_code=mobile_country_code,
                    number=mobile_number
                ),
                name=name.strip(),
                birthday=birthday,
                gender=gender,
                terms={
                    'privacy': True,
                    'policy': True
                },
                password=hashers.make_password(password),
                updated_at=datetime.utcnow()
            )
            await UserModel.update(
                {'_id': duplicated_user['_id'], 'enabled': True},
                {
                    '$set': doc
                },
                False, False
            )
        else:
            user = UserModel(raw_data=dict(
                mobile=dict(
                    country_code=mobile_country_code,
                    number=mobile_number
                ),
                name=name.strip(),
                birthday=birthday,
                gender=gender,
                terms={'privacy': True, 'policy': True}
            ))
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
            mobile_country_code = self.json_decoded_body.get('mobile_country_code', None)
            if not mobile_country_code:
                raise HTTPError(400, 'invalid mobile_country_code')
            mobile_number = self.json_decoded_body.get('mobile_number', None)
            if not mobile_number or len(mobile_number) < 9:
                raise HTTPError(400, 'invalid mobile_number')
            password = self.json_decoded_body.get('password', None)
            if not password or len(password) < 4:
                raise HTTPError(400, 'invalid password')
            user = await UserModel.find_one({'mobile.country_code': mobile_country_code, 'mobile.number': mobile_number, 'enabled': True})
            if not user:
                raise HTTPError(400, 'no exist user')
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
    @parse_argument([('mobile_country_code', str, None), ('mobile_number', str, None)])
    async def get(self, *args, **kwargs):
        parsed_args = kwargs.get('parsed_args')
        if not parsed_args['mobile_number'] or not parsed_args['mobile_country_code'] or len(parsed_args['mobile_number']) < 10:
            raise HTTPError(400, 'invalid mobile_number and mobile_country_code')
        if parsed_args['mobile_country_code'] == '82' and not parsed_args['mobile_number'].startswith('010'):
            raise HTTPError(400, 'invalid Korea mobile number')
        q = {
            'mobile.country_code': parsed_args['mobile_country_code'],
            'mobile.number': parsed_args['mobile_number'],
            'enabled': True
        }
        user = await UserModel.find_one(query=q)
        if not user:
            raise HTTPError(400, 'no exist user')
        res = dict()
        if 'terms' in user and user['terms']['privacy'] and user['terms']['policy']:
            res['terms'] = True
        else:
            res['terms'] = False
        self.response['data'] = res
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class AutoLoginHandler(JsonHandler):
    async def put(self, *args, **kwargs):
        mobile_country_code = self.json_decoded_body.get('mobile_country_code', None)
        if not mobile_country_code:
            raise HTTPError(400, 'invalid mobile_country_code')
        mobile_number = self.json_decoded_body.get('mobile_number', None)
        if not mobile_number:
            raise HTTPError(400, 'invalid mobile_number')
        content_oid = self.json_decoded_body.get('content_oid', None)
        if not content_oid:
            raise HTTPError(400, 'invalid content_oid')
        user = await UserModel.find_one({'mobile.country_code': mobile_country_code, 'mobile.number': mobile_number, 'enabled': True})
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
        LmsService().send(mobile_number, '티킷(TKIT)', 'http://%s:%s/autologin/%s' % (config['web']['host'], config['web']['port'], userautologin_oid))
        self.response['message'] = 'check your sms'
        self.response['is_sent_receiver'] = True
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


class SmsSendHandler(JsonHandler):
    async def put(self, *args, **kwargs):
        mobile = self.json_decoded_body.get('mobile', None)
        if not mobile or not isinstance(mobile, dict):
            raise HTTPError(400, self.set_error(1, 'mobile(object) is required'))
        if 'country_code' not in mobile or 'number' not in mobile:
            raise HTTPError(400, self.set_error(2, 'invalid moblie'))
        verify_code = hashers.generate_random_number(4)
        doc = {
            'mobile': mobile,
            'code': verify_code,
            'expired_at': datetime.utcnow() + timedelta(minutes=3)
        }
        sms_verify = SmsVerificationModel(raw_data=doc)
        _id = await sms_verify.insert()
        if mobile['country_code'] == '82':
            res = LmsService().send(mobile['number'], '티킷(TKIT)', '[티킷] 인증코드 %s' % verify_code)
            logging.info(res)
        else:
            if mobile['number'].startswith('0'):
                mobile['number'] = mobile['number'][1:]
            payload = {
                'type': 'unicode',
                'from': 'TKIT',
                'to': '%s%s' % (mobile['country_code'], mobile['number']),
                'text': '[티킷] 인증코드 %s' % verify_code
            }
            res = NexmoService().client.send_message(payload)
            logging.info(res)
            if res['messages'][0]['status'] != '0':
                raise HTTPError(400, self.set_error(3, '%s: %s' % (res['messages'][0]['status'], res['messages'][0]['error-text'])))
        self.response['data'] = res
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class SmsVerifyHandler(JsonHandler):
    async def put(self, *args, **kwargs):
        mobile = self.json_decoded_body.get('mobile', None)
        if not mobile or not isinstance(mobile, dict):
            raise HTTPError(400, self.set_error(1, 'mobile(object) is required'))
        code = self.json_decoded_body.get('code', None)
        if not code or len(code) != 4:
            raise HTTPError(400, self.set_error(2, 'invalid code(length is only 4 characters)'))
        sms_doc = {
            'mobile.country_code': mobile['country_code'],
            'mobile.number': mobile['number'],
            'code': code,
            'enabled': True
        }
        sms_verify = await SmsVerificationModel.find_one(sms_doc)
        if not sms_verify:
            raise HTTPError(400, self.set_error(3, 'no exist valid verification'))
        if datetime.utcnow() > sms_verify['expired_at']:
            raise HTTPError(400, self.set_error(4, 'expired verification code'))
        user_oid = await create_user_v2(mobile, '')
        session = UserSessionModel()
        session.data['user_oid'] = user_oid
        session_oid = await session.insert()
        self.response['data'] = {
            'usk': str(session_oid)
        }
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()
