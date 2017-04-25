# -*- coding: utf-8 -*-

from datetime import datetime
from bson import ObjectId

from tornado.web import HTTPError

from common.decorators import admin_auth_async, parse_argument

from handlers.base import JsonHandler
from models.user import UserModel

from common import hashers


class UserListHandler(JsonHandler):
    @admin_auth_async
    @parse_argument([('start', int, 0), ('size', int, 10), ('q', str, None)])
    async def get(self, *args, **kwargs):
        parsed_args = kwargs.get('parsed_args')
        q = dict()
        if 'q' in parsed_args and parsed_args['q']:
            q['$or'] = [
                {'name': {'$regex': parsed_args['q']}},
                {'email': {'$regex': parsed_args['q']}},
                {'mobile_number': {'$regex': parsed_args['q']}},
                {'gender': {'$regex': parsed_args['q']}},
                {'birthday': {'$regex': parsed_args['q']}},
                {'role': {'$regex': parsed_args['q']}}
            ]
        count = await UserModel.count(query=q)
        result = await UserModel.find(query=q, skip=parsed_args['start'], limit=parsed_args['size'])
        self.response['data'] = result
        self.response['count'] = count
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class UserHandler(JsonHandler):
    @admin_auth_async
    async def post(self, *args, **kwargs):
        # basic field
        role = self.json_decoded_body.get('role', None)
        if not role or len(role) == 0 or not isinstance(role, list):
            raise HTTPError(400, 'invalid role')
        for r in role:
            if r not in UserModel.ROLE:
                raise HTTPError(400, 'invalid role (user or broker)')
        name = self.json_decoded_body.get('name', None)
        if not name or len(name) == 0:
            raise HTTPError(400, 'invalid name')
        mobile_number = self.json_decoded_body.get('mobile_number', None)
        if not mobile_number or len(mobile_number) == 0:
            raise HTTPError(400, 'invalid mobile_number')

        # check duplicated user
        duplicated_user = await UserModel.find_one({'mobile_number': mobile_number})
        if duplicated_user:
            raise HTTPError(400, 'duplicated mobile_number')

        # create user model
        user = UserModel(raw_data=dict(
            name=name,
            mobile_number=mobile_number,
            role=role
        ))

        # for user
        if 'user' in role:
            email = self.json_decoded_body.get('email', None)
            if not email or len(email) == 0:
                raise HTTPError(400, 'invalid email')
            birthday = self.json_decoded_body.get('birthday', None)
            if not birthday or len(birthday) == 0:
                raise HTTPError(400, 'invalid birthday')
            gender = self.json_decoded_body.get('gender', None)
            if not gender or len(gender) == 0:
                raise HTTPError(400, 'invalid gender')
            user.data['email'] = email
            user.data['birthday'] = birthday
            user.data['gender'] = gender

        # for broker
        if 'broker' in role:
            password = self.json_decoded_body.get('password', None)
            if not password or len(password) == 0 or not hashers.validate_password(password):
                raise HTTPError(400, 'invalid password')
            user.set_password(password)

        await user.insert()
        self.response['data'] = user.data
        self.write_json()

    @admin_auth_async
    async def put(self, *args, **kwargs):
        _id = kwargs.get('_id', None)
        if not _id or len(_id) != 24:
            raise HTTPError(400, 'invalid _id')
        user = await UserModel.find_one({'_id': ObjectId(_id)})
        if not user:
            raise HTTPError(400, 'not exist _id')
        query = {
            '_id': ObjectId(_id)
        }
        self.json_decoded_body['updated_at'] = datetime.utcnow()
        document = {
            '$set': self.json_decoded_body
        }
        self.response['data'] = await UserModel.update(query, document)
        self.write_json()

    @admin_auth_async
    async def get(self, *args, **kwargs):
        _id = kwargs.get('_id', None)
        if not _id or len(_id) != 24:
            raise HTTPError(400, 'invalid _id')
        user = await UserModel.find_one({'_id': ObjectId(_id)})
        if not user:
            raise HTTPError(400, 'not exist _id')
        self.response['data'] = user
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()
