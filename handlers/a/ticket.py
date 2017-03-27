# -*- coding: utf-8 -*-

from datetime import datetime
from bson import ObjectId

from tornado.web import HTTPError

from common.decorators import admin_auth_async, parse_argument

from handlers.base import JsonHandler
from models.ticket import TicketTypeModel

from models import get_content, get_admin


class TicketTypeListHandler(JsonHandler):
    @admin_auth_async
    @parse_argument([('start', int, 0), ('size', int, 10), ('q', str, None)])
    async def get(self, *args, **kwargs):
        parsed_args = kwargs.get('parsed_args')
        if parsed_args['q']:
            q = {
                '$or': [
                    {'_id': self.current_user['_id']},
                    {'name': {'$regex': parsed_args['q']}},
                    {'desc': {'$regex': parsed_args['q']}}
                ]
            }
        else:
            q = {}
        count = await TicketTypeModel.count(query=q)
        result = await TicketTypeModel.find(query=q, skip=parsed_args['start'], limit=parsed_args['size'])
        for res in result:
            res['content'] = await get_content(res['content_oid'])
            res['user'] = await get_admin(res['user_oid'])
            res.pop('content_oid')
            res.pop('user_oid')
        self.response['data'] = result
        self.response['count'] = count
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class TicketTypeHandler(JsonHandler):
    @admin_auth_async
    async def post(self, *args, **kwargs):
        # basic field
        user_oid = self.current_user['_id']
        content_oid = self.json_decoded_body.get('content_oid', None)
        if not content_oid or len(content_oid) != 24:
            raise HTTPError(400, 'invalid content_oid')
        name = self.json_decoded_body.get('name', None)
        if not name or len(name) == 0:
            raise HTTPError(400, 'invalid name')
        price = self.json_decoded_body.get('price', None)
        if not price or not isinstance(price, int):
            raise HTTPError(400, 'invalid price')
        desc = self.json_decoded_body.get('desc', None)
        if not desc or len(desc) == 0:
            raise HTTPError(400, 'invalid desc')

        # create ticket type model
        ticket_type = TicketTypeModel(raw_data=dict(
            user_oid=user_oid,
            content_oid=ObjectId(content_oid),
            name=name,
            price=price,
            desc=desc
        ))

        await ticket_type.insert()
        self.response['data'] = ticket_type.data
        self.write_json()

    @admin_auth_async
    async def put(self, *args, **kwargs):
        _id = kwargs.get('_id', None)
        if not _id or len(_id) != 24:
            raise HTTPError(400, 'invalid _id')
        ticket_type = await TicketTypeModel.find_one({'_id': ObjectId(_id)})
        if not ticket_type:
            raise HTTPError(400, 'not exist _id')
        query = {
            '_id': ObjectId(_id),
            'user_oid': self.current_user['_id']
        }
        self.json_decoded_body['updated_at'] = datetime.utcnow()
        document = {
            '$set': self.json_decoded_body
        }
        self.response['data'] = await TicketTypeModel.update(query, document)
        self.write_json()

    @admin_auth_async
    async def get(self, *args, **kwargs):
        _id = kwargs.get('_id', None)
        if not _id or len(_id) != 24:
            raise HTTPError(400, 'invalid _id')
        ticket_type = await TicketTypeModel.find_one({'_id': ObjectId(_id), 'user_oid': self.current_user['_id']})
        if not ticket_type:
            raise HTTPError(400, 'not exist ticket type')
        self.response['data'] = ticket_type
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()
