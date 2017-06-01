# -*- coding: utf-8 -*-

from datetime import datetime
from bson import ObjectId

from tornado.web import HTTPError

from common.decorators import admin_auth_async, parse_argument
from common import hashers

from handlers.base import JsonHandler
from models.admin import AdminModel
from models.company import CompanyModel


def get_query_by_user(user=None):
    q = {'$and': []}
    if user['role'] == 'super':
        q['$and'].append(
            {
                '$or': [
                    {'role': 'super'},
                    {'role': 'admin'},
                    {'role': 'host'},
                    {'role': 'staff'}
                ]
            }
        )
    elif user['role'] == 'admin':
        q['$and'].append(
            {
                '$or': [
                    {'role': 'host'},
                    {'role': 'staff'}
                ]
            }
        )
    elif user['role'] == 'host':
        q['$and'].append(
            {
                '$or': [
                    {'role': 'staff'}
                ]
            }
        )
        q['$and'].append(
            {
                'company_oid': user['company_oid']
            }
        )
    elif user['role'] == 'staff':
        pass
    else:
        pass
    return q


class AdminListHandler(JsonHandler):
    @admin_auth_async
    @parse_argument([('start', int, 0), ('size', int, 10), ('q', str, None)])
    async def get(self, *args, **kwargs):
        parsed_args = kwargs.get('parsed_args')
        q = get_query_by_user(self.current_user)
        if not q['$and']:
            raise HTTPError(400, 'invalid role')
        if 'q' in parsed_args and parsed_args['q']:
            search_q = {'$or': [
                {'name': {'$regex': parsed_args['q']}},
                {'email': {'$regex': parsed_args['q']}},
                {'mobile_number': {'$regex': parsed_args['q']}},
                {'role': {'$regex': parsed_args['q']}}
            ]}
            q['$and'].append(search_q)
        count = await AdminModel.count(query=q)
        result = await AdminModel.find(query=q, skip=parsed_args['start'], limit=parsed_args['size'])
        for r in result:
            r['company'] = await AdminModel.get_id(r['company_oid'])
            r.pop('company_oid')
        self.response['data'] = result
        self.response['count'] = count
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class AdminHandler(JsonHandler):
    @admin_auth_async
    async def post(self, *args, **kwargs):
        role = self.json_decoded_body.get('role', None)
        if not role or len(role) == 0:
            raise HTTPError(400, 'invalid role')
        if role not in AdminModel.ROLE:
            raise HTTPError(400, 'invalid role (admin, host, staff and super)')
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
        duplicated_admin = await AdminModel.find_one({'email': email})
        if duplicated_admin:
            raise HTTPError(400, 'duplicated email')

        admin = AdminModel(raw_data=dict(
            email=email,
            mobile_number=mobile_number,
            name=name,
            role=role,
        ))
        admin.set_password(password)
        company_oid = self.json_decoded_body.get('company_oid', None)
        if company_oid and (role=='host' or role=='staff'):
            admin.data['company_oid'] = ObjectId(company_oid)
        await admin.insert()
        self.response['data'] = admin.data
        self.write_json()

    @admin_auth_async
    async def put(self, *args, **kwargs):
        _id = kwargs.get('_id', None)
        if not _id or len(_id) != 24:
            raise HTTPError(400, 'invalid _id')
        admin = await AdminModel.find_one({'_id': ObjectId(_id)})
        if not admin:
            raise HTTPError(400, 'not exist _id')
        query = {
            '_id': ObjectId(_id)
        }
        self.json_decoded_body['updated_at'] = datetime.utcnow()
        document = {
            '$set': self.json_decoded_body
        }
        document['$set']['company_oid'] = ObjectId(document['$set']['company_oid'])
        self.response['data'] = await AdminModel.update(query, document)
        self.write_json()

    @admin_auth_async
    async def get(self, *args, **kwargs):
        _id = kwargs.get('_id', None)
        if not _id or len(_id) != 24:
            raise HTTPError(400, 'invalid _id')
        admin = await AdminModel.find_one({'_id': ObjectId(_id)})
        if not admin:
            raise HTTPError(400, 'not exist _id')
        admin['company'] = await CompanyModel.get_id(admin['company_oid'])
        admin.pop('company_oid')
        self.response['data'] = admin
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class AdminPasswordHandler(JsonHandler):
    @admin_auth_async
    async def put(self, *args, **kwargs):
        _id = kwargs.get('_id', None)
        if not _id or len(_id) != 24:
            raise HTTPError(400, 'invalid _id')
        old_password = self.json_decoded_body.get('old_password', None)
        if not old_password or len(old_password) == 0 or not hashers.validate_password(old_password):
            raise HTTPError(400, 'invalid old_password')
        new_password_1 = self.json_decoded_body.get('new_password_1', None)
        if not new_password_1 or len(new_password_1) == 0 or not hashers.validate_password(new_password_1):
            raise HTTPError(400, 'invalid new_password_1')
        new_password_2 = self.json_decoded_body.get('new_password_2', None)
        if not new_password_2 or len(new_password_2) == 0 or not hashers.validate_password(new_password_2):
            raise HTTPError(400, 'invalid new_password_2')
        if new_password_1 != new_password_2:
            raise HTTPError(400, 'new password 1 and 2 not matched')
        admin = await AdminModel.find_one({'_id': ObjectId(_id)})
        if not admin:
            raise HTTPError(400, 'not exist _id')
        if not hashers.check_password(old_password, admin['password']):
            raise HTTPError(400, 'not correct old password')
        query = {
            '_id': ObjectId(_id)
        }
        document = {
            '$set': {
                'password': hashers.make_password(new_password_1),
                'updated_at': datetime.utcnow()
            }
        }
        self.response['data'] = await AdminModel.update(query, document)
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()
