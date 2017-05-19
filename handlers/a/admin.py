# -*- coding: utf-8 -*-

from datetime import datetime
from bson import ObjectId

from tornado.web import HTTPError

from common.decorators import admin_auth_async, parse_argument
from common import hashers

from handlers.base import JsonHandler
from models.admin import AdminModel


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
    elif role == 'staff':
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
                {'company': {'$regex': parsed_args['q']}},
                {'mobile_number': {'$regex': parsed_args['q']}},
                {'role': {'$regex': parsed_args['q']}}
            ]}
            q['$and'].append(search_q)
        count = await AdminModel.count(query=q)
        result = await AdminModel.find(query=q, skip=parsed_args['start'], limit=parsed_args['size'])
        self.response['data'] = result
        self.response['count'] = count
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class AdminHandler(JsonHandler):
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
            admin.data['company_oid'] = company_oid
        else:
            raise HTTPError(400, 'host and staff role needs company_oid')

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
        self.response['data'] = admin
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()
