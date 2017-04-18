# -*- coding: utf-8 -*-

from datetime import datetime
from bson import ObjectId

from tornado.web import HTTPError

from handlers.base import JsonHandler
from models.user import UserModel
from models.session import UserSessionModel

from common import hashers


class LoginHandler(JsonHandler):
    async def post(self, *args, **kwargs):
        self.clear_cookie(self.COOKIE_KEYS['USER_SESSION_KEY'])
        name = self.json_decoded_body.get('name', None)
        if not name or len(name) == 0:
            raise HTTPError(400, 'invalid name')
        mobile_number = self.json_decoded_body.get('mobile_number', None)
        if not mobile_number or len(mobile_number) == 0:
            raise HTTPError(400, 'invalid mobile_number')
        user = await UserModel.find_one({'name': name, 'mobile_number': mobile_number, 'enabled': True})
        if not user:
            raise HTTPError(400, 'no exist user')
        self.current_user = user
        session = UserSessionModel()
        session.data['user_oid'] = user['_id']
        session_oid = await session.insert()
        self.set_cookie(self.COOKIE_KEYS['USER_SESSION_KEY'], str(session_oid))
        self.response['data'] = user
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()
