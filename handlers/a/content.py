# -*- coding: utf-8 -*-

from datetime import datetime
from bson import ObjectId

from tornado.web import HTTPError

from common.decorators import admin_auth_async, parse_argument

from handlers.base import JsonHandler
from models.content import ContentModel

from common import hashers


class ContentListHandler(JsonHandler):
    @admin_auth_async
    @parse_argument([('start', int, 0), ('size', int, 10), ('q', str, None)])
    async def get(self, *args, **kwargs):
        parsed_args = kwargs.get('parsed_args')
        if parsed_args['q']:
            q = {
                '$or': [
                    {'user_oid': self.current_user['_id']},
                    {'name': {'$regex': parsed_args['q']}},
                    {'desc': {'$regex': parsed_args['q']}},
                    {'place': {'$regex': parsed_args['q']}},
                    {'genre': {'$regex': parsed_args['q']}},
                    {'lineup': {'$regex': parsed_args['q']}},
                    {'role': {'$regex': parsed_args['q']}}
                ]
            }
        else:
            q = {}
        count = await ContentModel.count(query=q)
        result = await ContentModel.find(query=q, skip=parsed_args['start'], limit=parsed_args['size'])
        self.response['data'] = result
        self.response['count'] = count
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class ContentHandler(JsonHandler):
    @admin_auth_async
    async def post(self, *args, **kwargs):
        # basic field
        user_oid = self.current_user['_id']
        name = self.json_decoded_body.get('name', None)
        if not name or len(name) == 0:
            raise HTTPError(400, 'invalid name')
        place = self.json_decoded_body.get('place', None)
        if not place or len(place) == 0:
            raise HTTPError(400, 'invalid place')

        # create content model
        content = ContentModel(raw_data=dict(
            user_oid=user_oid,
            name=name,
            place=place
        ))

        await content.insert()
        self.response['data'] = content.data
        self.write_json()

    @admin_auth_async
    async def put(self, *args, **kwargs):
        _id = kwargs.get('_id', None)
        if not _id or len(_id) != 24:
            raise HTTPError(400, 'invalid _id')
        content = await ContentModel.find_one({'_id': ObjectId(_id)})
        if not content:
            raise HTTPError(400, 'not exist _id')
        query = {
            '_id': ObjectId(_id),
            'user_oid': self.current_user['_id']
        }
        self.json_decoded_body['updated_at'] = datetime.utcnow()
        document = {
            '$set': self.json_decoded_body
        }
        self.response['data'] = await ContentModel.update(query, document)
        self.write_json()

    @admin_auth_async
    async def get(self, *args, **kwargs):
        _id = kwargs.get('_id', None)
        if not _id or len(_id) != 24:
            raise HTTPError(400, 'invalid _id')
        content = await ContentModel.find_one({'_id': ObjectId(_id), 'user_oid': self.current_user['_id']})
        if not content:
            raise HTTPError(400, 'not exist content')
        self.response['data'] = content
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()
