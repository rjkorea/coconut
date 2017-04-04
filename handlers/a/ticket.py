# -*- coding: utf-8 -*-

from datetime import datetime
from bson import ObjectId

from tornado.web import HTTPError

from common.decorators import admin_auth_async, parse_argument

from handlers.base import JsonHandler
from models.ticket import TicketTypeModel, TicketOrderModel

from models import get_content, get_admin, get_ticket_type


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
        self.response['data']['content'] = await get_content(self.response['data']['content_oid'])
        self.response['data']['user'] = await get_admin(self.response['data']['user_oid'])
        self.response['data'].pop('content_oid')
        self.response['data'].pop('user_oid')
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class TicketOrderListHandler(JsonHandler):
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
        count = await TicketOrderModel.count(query=q)
        result = await TicketOrderModel.find(query=q, skip=parsed_args['start'], limit=parsed_args['size'])
        for res in result:
            res['ticket_type'] = await get_ticket_type(res['ticket_type_oid'])
            res['user'] = await get_admin(res['user_oid'])
            res.pop('ticket_type_oid')
            res.pop('user_oid')
        self.response['data'] = result
        self.response['count'] = count
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class TicketOrderHandler(JsonHandler):
    @admin_auth_async
    async def post(self, *args, **kwargs):
        # basic field
        user_oid = self.current_user['_id']
        ticket_type_oid = self.json_decoded_body.get('ticket_type_oid', None)
        if not ticket_type_oid or len(ticket_type_oid) != 24:
            raise HTTPError(400, 'invalid ticket_type_oid')
        qty = self.json_decoded_body.get('qty', None)
        if not qty or not isinstance(qty, int):
            raise HTTPError(400, 'invalid qty')
        receiver = self.json_decoded_body.get('receiver', None)
        if not receiver or not isinstance(receiver, dict):
            raise HTTPError(400, 'invalid receiver')
        if 'mobile_number' not in receiver or 'name' not in receiver or 'access_code' not in receiver:
            raise HTTPError(400, 'invalid mobile_number | name | access_code')
        fee = self.json_decoded_body.get('fee', None)
        if not fee or not isinstance(fee, dict):
            raise HTTPError(400, 'invalid fee')
        if 'price' not in fee or 'method' not in fee:
            raise HTTPError(400, 'invalid price | method')
        expiry_date = self.json_decoded_body.get('expiry_date', None)
        if not expiry_date or len(expiry_date) == 0:
            raise HTTPError(400, 'invalid expiry_date')
        try:
            expiry_date = datetime.strptime(expiry_date, '%Y-%m-%dT%H:%M:%S')
        except ValueError as e:
            raise HTTPError(400, e)

        # create ticket order model
        ticket_order = TicketOrderModel(raw_data=dict(
            user_oid=user_oid,
            ticket_type_oid=ObjectId(ticket_type_oid),
            qty=qty,
            receiver=receiver,
            fee=fee,
            expiry_date=expiry_date
        ))
        parent_oid = self.json_decoded_body.get('parent_oid', None)
        if parent_oid:
            ticket_order.data['parent_oid'] = parent_oid

        await ticket_order.insert()
        self.response['data'] = ticket_order.data
        self.write_json()

    @admin_auth_async
    async def put(self, *args, **kwargs):
        _id = kwargs.get('_id', None)
        if not _id or len(_id) != 24:
            raise HTTPError(400, 'invalid _id')
        ticket_order = await TicketOrderModel.find_one({'_id': ObjectId(_id)})
        if not ticket_order:
            raise HTTPError(400, 'not exist _id')
        query = {
            '_id': ObjectId(_id),
            'user_oid': self.current_user['_id']
        }
        self.json_decoded_body['updated_at'] = datetime.utcnow()
        document = {
            '$set': self.json_decoded_body
        }
        self.response['data'] = await TicketOrderModel.update(query, document)
        self.write_json()

    @admin_auth_async
    async def get(self, *args, **kwargs):
        _id = kwargs.get('_id', None)
        if not _id or len(_id) != 24:
            raise HTTPError(400, 'invalid _id')
        ticket_order = await TicketOrderModel.find_one({'_id': ObjectId(_id), 'user_oid': self.current_user['_id']})
        if not ticket_order:
            raise HTTPError(400, 'not exist ticket order')
        self.response['data'] = ticket_order
        self.response['data']['ticket_type'] = await get_ticket_type(self.response['data']['ticket_type_oid'])
        self.response['data']['user'] = await get_admin(self.response['data']['user_oid'])
        self.response['data'].pop('ticket_type_oid')
        self.response['data'].pop('user_oid')
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()
