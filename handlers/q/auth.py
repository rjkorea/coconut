# -*- coding: utf-8 -*-

from datetime import datetime
from bson import ObjectId

from tornado.web import HTTPError

from handlers.base import JsonHandler
from models.admin import AdminModel
from models.session import AdminSessionModel

from common import hashers


class LoginHandler(JsonHandler):
    async def post(self, *args, **kwargs):
        self.clear_cookie(self.COOKIE_KEYS['SESSION_KEY'])
        email = self.json_decoded_body.get('email', None)
        if not email or len(email) == 0:
            raise HTTPError(400, 'invalid email')
        password = self.json_decoded_body.get('password', None)
        if not password or len(password) == 0 or not hashers.validate_password(password):
            raise HTTPError(400, 'invalid password')
        admin = await AdminModel.find_one(query={'email': email, 'enabled': True}, fields=[('name'), ('email'), ('company_oid'), ('password')])
        if not admin:
            raise HTTPError(400, 'no exist admin user')
        if not hashers.check_password(password, admin['password']):
            raise HTTPError(400, 'invalid password')
        self.current_user = admin
        session = AdminSessionModel()
        session.data['admin_oid'] = admin['_id']
        session_oid = await session.insert()
        admin['csk'] = str(session_oid)
        del admin['password']
        self.response['data'] = admin
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()
