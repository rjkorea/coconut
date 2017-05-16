# -*- coding: utf-8 -*-

from datetime import datetime
from bson import ObjectId

from tornado.web import HTTPError

from common.decorators import admin_auth_async, parse_argument

from handlers.base import JsonHandler
from models.company import CompanyModel


class CompanyListHandler(JsonHandler):
    @admin_auth_async
    @parse_argument([('start', int, 0), ('size', int, 10), ('q', str, None)])
    async def get(self, *args, **kwargs):
        parsed_args = kwargs.get('parsed_args')
        q = dict()
        if 'q' in parsed_args and parsed_args['q']:
            q['$or'] = [
                {'name': {'$regex': parsed_args['q']}},
                {'contact.name': {'$regex': parsed_args['q']}},
                {'contact.email': {'$regex': parsed_args['q']}},
                {'contact.mobile_number': {'$regex': parsed_args['q']}}
            ]
        count = await CompanyModel.count(query=q)
        result = await CompanyModel.find(query=q, skip=parsed_args['start'], limit=parsed_args['size'])
        self.response['data'] = result
        self.response['count'] = count
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class CompanyHandler(JsonHandler):
    @admin_auth_async
    async def post(self, *args, **kwargs):
        # basic field
        name = self.json_decoded_body.get('name', None)
        if not name or len(name) == 0:
            raise HTTPError(400, 'invalid name')
        contact = self.json_decoded_body.get('contact', None)
        if not contact or not isinstance(contact, dict):
            raise HTTPError(400, 'invalid contact')
        company = CompanyModel(raw_data=dict(
            name=name,
            contact=contact,
            admin_oid=self.current_user['_id']
        ))
        await company.insert()
        self.response['data'] = company.data
        self.write_json()

    @admin_auth_async
    async def put(self, *args, **kwargs):
        _id = kwargs.get('_id', None)
        if not _id or len(_id) != 24:
            raise HTTPError(400, 'invalid _id')
        company = await CompanyModel.find_one({'_id': ObjectId(_id)})
        if not company:
            raise HTTPError(400, 'not exist _id')
        query = {
            '_id': ObjectId(_id)
        }
        self.json_decoded_body['updated_at'] = datetime.utcnow()
        document = {
            '$set': self.json_decoded_body
        }
        self.response['data'] = await CompanyModel.update(query, document)
        self.write_json()

    @admin_auth_async
    async def get(self, *args, **kwargs):
        _id = kwargs.get('_id', None)
        if not _id or len(_id) != 24:
            raise HTTPError(400, 'invalid _id')
        company = await CompanyModel.find_one({'_id': ObjectId(_id)})
        if not company:
            raise HTTPError(400, 'not exist _id')
        self.response['data'] = company
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()
