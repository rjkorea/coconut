# -*- coding: utf-8 -*-

from datetime import datetime
from bson import ObjectId

from tornado.web import HTTPError

from common.decorators import admin_auth_async, parse_argument
from common import constants

from handlers.base import JsonHandler
from models.ticket import TicketTypeModel, TicketOrderModel, TicketModel
from models.content import ContentModel

from models import get_content, get_admin, get_user
from models import get_ticket_type, get_ticket_order
from models import create_ticket, create_broker
from models import send_sms


class TicketTypeListHandler(JsonHandler):
    @admin_auth_async
    @parse_argument([('start', int, 0), ('size', int, 10), ('q', str, None),
        ('content_oid', str, None), ('admin_oid', str, None)])
    async def get(self, *args, **kwargs):
        parsed_args = kwargs.get('parsed_args')
        q = dict()
        if 'content_oid' in parsed_args and parsed_args['content_oid']:
            q['content_oid'] = ObjectId(parsed_args['content_oid'])
        if 'admin_oid' in parsed_args and parsed_args['admin_oid']:
            q['admin_oid'] = ObjectId(parsed_args['admin_oid'])
        if 'q' in parsed_args and parsed_args['q']:
            q['$or'] = [
                {'name': {'$regex': parsed_args['q']}},
                {'desc': {'$regex': parsed_args['q']}}
            ]
        count = await TicketTypeModel.count(query=q)
        result = await TicketTypeModel.find(query=q, skip=parsed_args['start'], limit=parsed_args['size'])
        for res in result:
            res['content'] = await get_content(res['content_oid'])
            res['admin'] = await get_admin(res['admin_oid'])
            res.pop('content_oid')
            res.pop('admin_oid')
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
        admin_oid = self.current_user['_id']
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
        day = self.json_decoded_body.get('day', None)
        if not day or not isinstance(day, int):
            raise HTTPError(400, 'invalid day')

        # create ticket type model
        ticket_type = TicketTypeModel(raw_data=dict(
            admin_oid=admin_oid,
            content_oid=ObjectId(content_oid),
            name=name,
            price=price,
            desc=desc,
            day=day
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
            'admin_oid': self.current_user['_id']
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
        ticket_type = await TicketTypeModel.find_one({'_id': ObjectId(_id)})
        if not ticket_type:
            raise HTTPError(400, 'not exist ticket type')
        self.response['data'] = ticket_type
        self.response['data']['content'] = await get_content(self.response['data']['content_oid'])
        self.response['data']['admin'] = await get_admin(self.response['data']['admin_oid'])
        self.response['data'].pop('content_oid')
        self.response['data'].pop('admin_oid')
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class TicketOrderListHandler(JsonHandler):
    @admin_auth_async
    @parse_argument([('start', int, 0), ('size', int, 10), ('q', str, None),
        ('content_oid', str, None), ('admin_oid', str, None)])
    async def get(self, *args, **kwargs):
        parsed_args = kwargs.get('parsed_args')
        q = dict()
        if 'content_oid' in parsed_args and parsed_args['content_oid']:
            q['content_oid'] = ObjectId(parsed_args['content_oid'])
        if 'admin_oid' in parsed_args and parsed_args['admin_oid']:
            q['admin_oid'] = ObjectId(parsed_args['admin_oid'])
        if 'q' in parsed_args and parsed_args['q']:
            q['$or'] = [
                {'name': {'$regex': parsed_args['q']}},
                {'desc': {'$regex': parsed_args['q']}}
            ]
        count = await TicketOrderModel.count(query=q)
        result = await TicketOrderModel.find(query=q, skip=parsed_args['start'], limit=parsed_args['size'])
        for res in result:
            res['ticket_type'] = await get_ticket_type(res['ticket_type_oid'])
            res['admin'] = await get_admin(res['admin_oid'])
            res.pop('ticket_type_oid')
            res.pop('admin_oid')
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
        admin_oid = self.current_user['_id']
        content_oid = self.json_decoded_body.get('content_oid', None)
        if not content_oid or len(content_oid) != 24:
            raise HTTPError(400, 'invalid content_oid')
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
        expiry_date = self.json_decoded_body.get('expiry_date', None)
        if not expiry_date or len(expiry_date) == 0:
            raise HTTPError(400, 'invalid expiry_date')
        try:
            expiry_date = datetime.strptime(expiry_date, '%Y-%m-%dT%H:%M:%S')
        except ValueError as e:
            raise HTTPError(400, e)

        # create ticket order model
        ticket_order = TicketOrderModel(raw_data=dict(
            admin_oid=admin_oid,
            content_oid=content_oid,
            ticket_type_oid=ObjectId(ticket_type_oid),
            qty=qty,
            receiver=receiver,
            expiry_date=expiry_date
        ))
        parent_oid = self.json_decoded_body.get('parent_oid', None)
        if parent_oid:
            ticket_order.data['parent_oid'] = parent_oid
        fee = self.json_decoded_body.get('fee', None)
        if fee:
            if 'price' not in fee or 'method' not in fee:
                raise HTTPError(400, 'invalid price | method')
            ticket_order.data['fee'] = fee

        await ticket_order.insert()
        await create_ticket(ticket_order.data)
        is_created_broker = await create_broker(ticket_order.data['receiver'])
        self.response['data'] = ticket_order.data
        self.response['is_created_broker'] = is_created_broker
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
            'admin_oid': self.current_user['_id']
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
        ticket_order = await TicketOrderModel.find_one({'_id': ObjectId(_id)})
        if not ticket_order:
            raise HTTPError(400, 'not exist ticket order')
        self.response['data'] = ticket_order
        self.response['data']['ticket_type'] = await get_ticket_type(self.response['data']['ticket_type_oid'])
        self.response['data']['admin'] = await get_admin(self.response['data']['admin_oid'])
        self.response['data'].pop('ticket_type_oid')
        self.response['data'].pop('admin_oid')
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class TicketOrderSendHandler(JsonHandler):
    @admin_auth_async
    async def put(self, *args, **kwargs):
        _id = kwargs.get('_id', None)
        if not _id or len(_id) != 24:
            raise HTTPError(400, 'invalid _id')
        ticket_order = await TicketOrderModel.find_one({'_id': ObjectId(_id)})
        if not ticket_order:
            raise HTTPError(400, 'not exist _id')
        ticket_type = await TicketTypeModel.find_one({'_id': ticket_order['ticket_type_oid']})
        content = await ContentModel.find_one({'_id': ticket_type['content_oid']})
        # send SMS
        is_sent_receiver = await send_sms(
            {
                'type': 'unicode',
                'from': 'tkit',
                'to': ticket_order['receiver']['mobile_number'],
                'text': constants.TICKET_ORDER_INFO_MSG.format(content['name'], 'http://tkit.me', ticket_order['receiver']['access_code'])
                        + '\n' + constants.TICKET_ORDER_WARN_MSG
            }
        )
        self.response['data'] = ticket_order
        self.response['is_sent_receiver'] = is_sent_receiver
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class TicketListHandler(JsonHandler):
    @admin_auth_async
    @parse_argument([('start', int, 0), ('size', int, 10), ('q', str, None), ('user_oid', str, None)])
    async def get(self, *args, **kwargs):
        parsed_args = kwargs.get('parsed_args')
        if parsed_args['q']:
            q = {
                '$or': [
                    {'status': {'$regex': parsed_args['q']}}
                ]
            }
        elif parsed_args['user_oid']:
            q = {
                'user_oid': ObjectId(parsed_args['user_oid'])
            }
        else:
            q = {}
        count = await TicketModel.count(query=q)
        result = await TicketModel.find(query=q, skip=parsed_args['start'], limit=parsed_args['size'])
        for res in result:
            res['ticket_order'] = await get_ticket_order(res['ticket_order_oid'])
            res.pop('ticket_order_oid')
            if 'user_oid' in res:
                res['user'] = await get_user(res['user_oid'])
                res.pop('user_oid')
        self.response['data'] = result
        self.response['count'] = count
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class TicketHandler(JsonHandler):
    @admin_auth_async
    async def post(self, *args, **kwargs):
        self.response['message'] = 'Not implement'
        self.write_json()

    @admin_auth_async
    async def put(self, *args, **kwargs):
        _id = kwargs.get('_id', None)
        if not _id or len(_id) != 24:
            raise HTTPError(400, 'invalid _id')
        ticket = await TicketModel.find_one({'_id': ObjectId(_id)})
        if not ticket:
            raise HTTPError(400, 'not exist _id')
        query = {
            '_id': ObjectId(_id)
        }
        self.json_decoded_body['updated_at'] = datetime.utcnow()
        document = {
            '$set': self.json_decoded_body
        }
        self.response['data'] = await TicketModel.update(query, document)
        self.write_json()

    @admin_auth_async
    async def get(self, *args, **kwargs):
        _id = kwargs.get('_id', None)
        if not _id or len(_id) != 24:
            raise HTTPError(400, 'invalid _id')
        ticket = await TicketModel.find_one({'_id': ObjectId(_id)})
        if not ticket:
            raise HTTPError(400, 'not exist ticket')
        self.response['data'] = ticket
        self.response['data']['ticket_order'] = await get_ticket_order(self.response['data']['ticket_order_oid'])
        self.response['data'].pop('ticket_order_oid')
        if 'user_oid' in self.response['data']:
            self.response['data']['user'] = await get_user(self.response['data']['user_oid'])
            self.response['data'].pop('user_oid')
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()
