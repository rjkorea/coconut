# -*- coding: utf-8 -*-

from datetime import datetime
from bson import ObjectId

from common.decorators import admin_auth_async, parse_argument

from handlers.base import JsonHandler
from models.admin import AdminModel


class AdminListHandler(JsonHandler):
    @admin_auth_async
    @parse_argument([('start', int, 0), ('size', int, 10), ('q', str, None)])
    async def get(self, *args, **kwargs):
        parsed_args = kwargs.get('parsed_args')
        if parsed_args['q']:
            q = {
                '$or': [
                    {'name': {'$regex': parsed_args['q']}},
                    {'email': {'$regex': parsed_args['q']}},
                    {'company': {'$regex': parsed_args['q']}},
                    {'mobile_number': {'$regex': parsed_args['q']}},
                    {'role': {'$regex': parsed_args['q']}}
                ]
            }
        else:
            q = {}
        count = await AdminModel.count(query=q)
        result = await AdminModel.find(query=q, skip=parsed_args['start'], limit=parsed_args['size'])
        self.response['data'] = result
        self.response['count'] = count
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()

class AdminHandler(JsonHandler):
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
