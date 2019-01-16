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


class SignupPersonalHandler(JsonHandler):
    async def post(self, *args, **kwargs):
        email = self.json_decoded_body.get('email', None)
        if not email or len(email) == 0:
            raise HTTPError(400, 'invalid email')
        duplicated_admin = await AdminModel.find_one({'email': email})
        if duplicated_admin:
            raise HTTPError(400, 'duplicated email')
        name = self.json_decoded_body.get('name', None)
        if not name or len(name) == 0:
            raise HTTPError(400, 'invalid name')
        last_name = self.json_decoded_body.get('last_name', None)
        if not last_name or len(last_name) == 0:
            raise HTTPError(400, 'invalid last_name')
        mobile_number = self.json_decoded_body.get('mobile_number', None)
        if not mobile_number or len(mobile_number) == 0:
            raise HTTPError(400, 'invalid mobile_number')
        birthday = self.json_decoded_body.get('birthday', None)
        if not birthday or len(birthday) < 8:
            raise HTTPError(400, 'invalid birthday')
        password = self.json_decoded_body.get('password', None)
        if not password or len(password) == 0 or not hashers.validate_password(password):
            raise HTTPError(400, 'invalid password')
        gender = self.json_decoded_body.get('gender', None)
        if not gender or len(gender) == 0:
            raise HTTPError(400, 'invalid gender')
        bank = self.json_decoded_body.get('bank', None)
        company = CompanyModel(raw_data=dict(
            name='%s %s' % (last_name, name),
            contact=dict(
                name='%s %s' % (last_name, name),
                mobile_number=mobile_number,
                email=email
            ),
            enabled=True
        ))
        company_oid = await company.insert()
        admin = AdminModel(raw_data=dict(
            role='host',
            type='personal',
            email=email,
            name=name,
            last_name=last_name,
            mobile_number=mobile_number,
            birthday=birthday,
            gender=gender,
            bank=bank,
            company_oid=ObjectId(company_oid)
        ))
        admin.set_password(password)
        await admin.insert()
        self.response['data'] = 'OK'
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class SignupBusinessHandler(JsonHandler):
    async def post(self, *args, **kwargs):
        email = self.json_decoded_body.get('email', None)
        if not email or len(email) == 0:
            raise HTTPError(400, 'invalid email')
        duplicated_admin = await AdminModel.find_one({'email': email})
        if duplicated_admin:
            raise HTTPError(400, 'duplicated email')
        name = self.json_decoded_body.get('name', None)
        if not name or len(name) == 0:
            raise HTTPError(400, 'invalid name')
        password = self.json_decoded_body.get('password', None)
        if not password or len(password) == 0 or not hashers.validate_password(password):
            raise HTTPError(400, 'invalid password')
        business_license = self.json_decoded_body.get('business_license', None)
        if not business_license or len(business_license) == 0:
            raise HTTPError(400, 'invalid business_license')
        president = self.json_decoded_body.get('president', None)
        if not president or len(president) == 0:
            raise HTTPError(400, 'invalid president')
        bank = self.json_decoded_body.get('bank', None)
        if not bank or len(bank) == 0:
            raise HTTPError(400, 'invalid bank')
        fax = self.json_decoded_body.get('fax', None)
        if not fax or len(fax) == 0:
            raise HTTPError(400, 'invalid fax')
        tel = self.json_decoded_body.get('tel', None)
        if not tel or len(tel) == 0:
            raise HTTPError(400, 'invalid tel')
        company = CompanyModel(raw_data=dict(
            name=name,
            contact=dict(
                name=name,
                mobile_number=tel,
                email=email
            ),
            enabled=True
        ))
        company_oid = await company.insert()
        admin = AdminModel(raw_data=dict(
            role='host',
            type='business',
            email=email,
            name=name,
            business_license=business_license,
            president=president,
            bank=bank,
            fax=fax,
            tel=tel,
            company_oid=ObjectId(company_oid)
        ))
        admin.set_password(password)
        await admin.insert()
        self.response['data'] = 'OK'
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
        data = {
            '_id': admin['_id'],
            'name': admin['name'],
            'csk': str(session_oid),
            'role': admin['role'],
            'company_name': company['name'],
            'company_oid': admin['company_oid'],
            'login_at': now
        }
        if 'tablet_code' in admin:
            data['tablet_code'] = admin['tablet_code']
        self.response['data'] = data
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()
