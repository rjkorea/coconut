# -*- coding: utf-8 -*-

from datetime import datetime
from bson import ObjectId

from tornado.web import HTTPError

from handlers.base import JsonHandler
from models.admin import AdminModel
from models.session import AdminSessionModel

from common import hashers


class RegisterHandler(JsonHandler):
    async def post(self, *args, **kwargs):
        email = self.json_decoded_body.get('email', None)
        if not email or len(email) == 0:
            raise HTTPError(400, 'invalid email')
        name = self.json_decoded_body.get('name', None)
        if not name or len(name) == 0:
            raise HTTPError(400, 'invalid name')
        password = self.json_decoded_body.get('password', None)
        if not password or len(password) == 0 or not hashers.validate_password(password):
            raise HTTPError(400, 'invalid password')
        password2 = self.json_decoded_body.get('password2', None)
        if not password or len(password) == 0 or not hashers.validate_password(password):
            raise HTTPError(400, 'invalid password2')
        if password != password2:
            raise HTTPError(400, 'password and password2 not matched')
        duplicated_admin = await AdminModel.find_one({'email': email})
        if duplicated_admin:
            raise HTTPError(400, 'duplicated email')
        admin = AdminModel(raw_data=dict(
            email=email,
            name=name
        ))
        admin.set_password(password)
        await admin.insert()
        self.response['data'] = admin.data
        self.write_json()


class LoginHandler(JsonHandler):
    async def post(self, *args, **kwargs):
        self.clear_cookie(self.COOKIE_KEYS['SESSION_KEY'])
        email = self.json_decoded_body.get('email', None)
        if not email or len(email) == 0:
            raise HTTPError(400, 'invalid email')
        password = self.json_decoded_body.get('password', None)
        if not password or len(password) == 0 or not hashers.validate_password(password):
            raise HTTPError(400, 'invalid password')
        admin = await AdminModel.find_one({'email': email})
        if not admin:
            raise HTTPError(400, 'no exist admin user')
        if not hashers.check_password(password, admin['password']):
            raise HTTPError(400, 'invalid password')
        self.current_user = admin
        session = AdminSessionModel()
        session.data['admin_oid'] = admin['_id']
        session_oid = await session.insert()
        self.set_cookie(self.COOKIE_KEYS['SESSION_KEY'], str(session_oid))
        # self.response['message'] = 'OK'
        self.response['data'] = dict(
            csk=str(session_oid),
            admin=admin
            )
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()
