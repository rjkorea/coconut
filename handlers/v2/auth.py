# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from bson import ObjectId
import jwt

from tornado.web import HTTPError

from handlers.base import JsonHandler
from models.user import UserModel

from common import hashers


class LoginHandler(JsonHandler):
    async def post(self, *args, **kwargs):
        name = self.json_decoded_body.get('name', None)
        if not name or len(name) == 0:
            raise HTTPError(400, 'invalid name')
        mobile = self.json_decoded_body.get('mobile', None)
        if not mobile or not isinstance(mobile, dict):
            raise HTTPError(400, 'invalid mobile')
        password = self.json_decoded_body.get('password', None)
        if not password or len(password) == 0 or not hashers.validate_user_password(password):
            raise HTTPError(400, 'invalid password')
        mobile_number = '%s%s' % (mobile['country_code'], mobile['number'][1:])
        user = await UserModel.find_one({'name': name, 'enabled': True, 'mobile_number': mobile_number})
        if not user:
            raise HTTPError(400, 'no exist user')
        if not hashers.check_password(password, user['password']):
            raise HTTPError(400, 'invalid password')
        now = datetime.utcnow()
        payload = dict(
            exp=now+timedelta(days=1),
            iat=now,
            user_oid=str(user['_id'])
        )
        access_token = jwt.encode(payload, 'tkitcoconut', algorithm='HS256').decode('utf-8')
        self.response['data'] = { 'access_token': access_token }
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()
