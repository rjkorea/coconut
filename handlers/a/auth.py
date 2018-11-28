# -*- coding: utf-8 -*-

from datetime import datetime
from bson import ObjectId

from tornado.web import HTTPError

from handlers.base import JsonHandler
from models.admin import AdminModel
from models.company import CompanyModel
from models.session import AdminSessionModel

from common import hashers


class RegisterHandler(JsonHandler):
    async def post(self, *args, **kwargs):
        role = self.json_decoded_body.get('role', None)
        if not role or len(role) == 0 or not isinstance(role, list):
            raise HTTPError(400, 'invalid role')
        email = self.json_decoded_body.get('email', None)
        if not email or len(email) == 0:
            raise HTTPError(400, 'invalid email')
        name = self.json_decoded_body.get('name', None)
        if not name or len(name) == 0:
            raise HTTPError(400, 'invalid name')
        mobile_number = self.json_decoded_body.get('mobile_number', None)
        if not mobile_number or len(mobile_number) == 0:
            raise HTTPError(400, 'invalid mobile_number')
        password = self.json_decoded_body.get('password', None)
        if not password or len(password) == 0 or not hashers.validate_password(password):
            raise HTTPError(400, 'invalid password')
        password2 = self.json_decoded_body.get('password2', None)
        if not password or len(password) == 0 or not hashers.validate_password(password):
            raise HTTPError(400, 'invalid password2')
        if password != password2:
            raise HTTPError(400, 'password and password2 not matched')
        for r in role:
            if r not in AdminModel.ROLE:
                raise HTTPError(400, 'invalid role (admin or host)')
        duplicated_admin = await AdminModel.find_one({'email': email})
        if duplicated_admin:
            raise HTTPError(400, 'duplicated email')
        admin = AdminModel(raw_data=dict(
            email=email,
            name=name,
            role=role
        ))
        if 'host' in role or 'pro' in role:
            mobile_number = self.json_decoded_body.get('mobile_number', None)
            if not mobile_number or len(mobile_number) == 0:
                raise HTTPError(400, 'invalid mobile_number')
            admin.data['mobile_number'] = mobile_number
        admin.set_password(password)
        await admin.insert()
        self.response['data'] = admin.data
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
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
        admin = await AdminModel.find_one({'email': email, 'enabled': True})
        if not admin:
            raise HTTPError(400, 'no exist admin user')
        if not hashers.check_password(password, admin['password']):
            raise HTTPError(400, 'invalid password')
        self.current_user = admin
        now = datetime.utcnow()
        session = AdminSessionModel()
        session.data['admin_oid'] = admin['_id']
        session_oid = await session.insert()
        company = await CompanyModel.get_id(admin['company_oid'])
        self.response['data'] = {
            '_id': admin['_id'],
            'name': admin['name'],
            'csk': str(session_oid),
            'role': admin['role'],
            'tablet_code': admin['tablet_code'],
            'company_name': company['name'],
            'login_at': now
        }
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()
