# -*- coding: utf-8 -*-

from datetime import datetime
from bson import ObjectId

from tornado.web import HTTPError

from common.decorators import admin_auth_async, parse_argument
from common import constants

from handlers.base import JsonHandler
from models.ticket import TicketTypeModel, TicketOrderModel, TicketModel, TicketLogModel
from models.content import ContentModel
from models.admin import AdminModel
from models.user import UserModel

from models import create_ticket, create_broker, create_user
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
            res['content'] = await ContentModel.get_id(res['content_oid'])
            res['admin'] = await AdminModel.get_id(res['admin_oid'])
            res.pop('content_oid')
            res.pop('admin_oid')
            res['ticket_order_cnt'] = await TicketOrderModel.count({'ticket_type_oid': ObjectId(res['_id'])})
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
        type = self.json_decoded_body.get('type', None)
        if not type or type not in TicketTypeModel.TICKET_TYPE:
            raise HTTPError(400, 'invalid type')
        name = self.json_decoded_body.get('name', None)
        if not name or len(name) == 0:
            raise HTTPError(400, 'invalid name')
        desc = self.json_decoded_body.get('desc', None)
        color = self.json_decoded_body.get('color', None)
        expiry_date = self.json_decoded_body.get('expiry_date', None)
        if not expiry_date:
            raise HTTPError(400, 'invalid expiry date')
        price = self.json_decoded_body.get('price', 0)
        ticket_type = TicketTypeModel(raw_data=dict(
            admin_oid=admin_oid,
            content_oid=ObjectId(content_oid),
            type=type,
            name=name,
            desc=desc,
            color=color,
            expiry_date=datetime.strptime(expiry_date, '%Y-%m-%dT%H:%M:%S'),
            price=price
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
            '_id': ObjectId(_id)
        }
        self.json_decoded_body['expiry_date'] = datetime.strptime(self.json_decoded_body['expiry_date'], '%Y-%m-%dT%H:%M:%S')
        self.json_decoded_body['updated_at'] = datetime.utcnow()
        document = {
            '$set': self.json_decoded_body
        }
        self.response['data'] = await TicketTypeModel.update(query, document, False, False)
        await TicketOrderModel.update(
            {'ticket_type_oid': ObjectId(_id)},
            {
                '$set': {
                    'expiry_date': self.json_decoded_body['expiry_date'],
                    'updated_at': self.json_decoded_body['updated_at']
                }
            },
            False, True)
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
        self.response['data']['content'] = await ContentModel.get_id(self.response['data']['content_oid'])
        self.response['data']['admin'] = await AdminModel.get_id(self.response['data']['admin_oid'])
        self.response['data'].pop('content_oid')
        self.response['data'].pop('admin_oid')
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class TicketOrderListHandler(JsonHandler):
    @admin_auth_async
    @parse_argument([('start', int, 0), ('size', int, 10), ('q', str, None),
        ('content_oid', str, None), ('admin_oid', str, None), ('ticket_type_oid', str, None)])
    async def get(self, *args, **kwargs):
        parsed_args = kwargs.get('parsed_args')
        q = dict()
        if 'content_oid' in parsed_args and parsed_args['content_oid']:
            q['content_oid'] = ObjectId(parsed_args['content_oid'])
        if 'admin_oid' in parsed_args and parsed_args['admin_oid']:
            q['admin_oid'] = ObjectId(parsed_args['admin_oid'])
        if 'ticket_type_oid' in parsed_args and parsed_args['ticket_type_oid']:
            q['ticket_type_oid'] = ObjectId(parsed_args['ticket_type_oid'])
        if 'q' in parsed_args and parsed_args['q']:
            q['$or'] = [
                {'name': {'$regex': parsed_args['q']}},
                {'desc': {'$regex': parsed_args['q']}}
            ]
        count = await TicketOrderModel.count(query=q)
        result = await TicketOrderModel.find(query=q, skip=parsed_args['start'], limit=parsed_args['size'])
        for res in result:
            res['ticket_type'] = await TicketTypeModel.get_id(res['ticket_type_oid'])
            res['admin'] = await AdminModel.get_id(res['admin_oid'])
            res['content'] = await ContentModel.get_id(res['content_oid'])
            res.pop('ticket_type_oid')
            res.pop('admin_oid')
            res.pop('content_oid')
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
        if 'mobile_number' not in receiver or 'name' not in receiver:
            raise HTTPError(400, 'invalid mobile_number | name')
        receiver['mobile_number'] = receiver['mobile_number'].strip()
        if receiver['mobile_number'].startswith('82'):
            if receiver['mobile_number'][2:4] != '10' or len(receiver['mobile_number'][4:]) < 7 or len(receiver['mobile_number'][4:]) > 8:
                raise HTTPError(400, 'incorrect mobile number format')
        receiver['name'] = receiver['name'].strip()
        expiry_date = self.json_decoded_body.get('expiry_date', None)
        if not expiry_date:
            raise HTTPError(400, 'invalid expiry_date')
        receiver['sms'] = {
            'count': 0
        }
        ticket_type = await TicketTypeModel.get_id(ObjectId(ticket_type_oid))
        # create ticket order model
        ticket_order = TicketOrderModel(raw_data=dict(
            admin_oid=admin_oid,
            content_oid=ObjectId(content_oid),
            ticket_type_oid=ObjectId(ticket_type_oid),
            type=ticket_type['type'],
            qty=qty,
            receiver=receiver,
            expiry_date=datetime.fromtimestamp(expiry_date)
        ))
        fee = self.json_decoded_body.get('fee', None)
        if fee:
            if 'price' not in fee or 'method' not in fee:
                raise HTTPError(400, 'invalid price | method')
            ticket_order.data['fee'] = fee
        slug = self.json_decoded_body.get('slug', None)
        if slug:
            duplicated_order = await TicketOrderModel.find_one({'slug': slug})
            if duplicated_order:
                raise HTTPError(400, 'duplicated slug')
            ticket_order.data['slug'] = slug

        broker_oid = await create_broker(ticket_order.data['receiver'])
        ticket_order.data['user_oid'] = broker_oid
        await ticket_order.insert()
        await create_ticket(ticket_order.data)
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
        self.response['data']['ticket_type'] = await TicketTypeModel.get_id(self.response['data']['ticket_type_oid'])
        self.response['data']['admin'] = await AdminModel.get_id(self.response['data']['admin_oid'])
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
        sms_message = self.json_decoded_body.get('sms_message', None)
        if not sms_message or len(sms_message) == 0:
            raise HTTPError(400, 'invalid sms_message')
        ticket_order = await TicketOrderModel.find_one({'_id': ObjectId(_id)})
        if not ticket_order:
            raise HTTPError(400, 'not exist _id')
        await TicketModel.update({'ticket_order_oid': ticket_order['_id'], 'status': TicketModel.Status.pend.name}, {'$set': {'status': TicketModel.Status.send.name}}, False, True)
        # send SMS
        is_sent_receiver = await send_sms(
            {
                'type': 'unicode',
                'from': 'tkit',
                'to': ticket_order['receiver']['mobile_number'],
                'text': sms_message
            }
        )
        if is_sent_receiver:
            await TicketOrderModel.update({'_id': ticket_order['_id']}, {'$set': {'receiver.sms.count': ticket_order['receiver']['sms']['count']+1, 'receiver.sms.sent_at': datetime.utcnow()}}, False, False)
        self.response['data'] = ticket_order
        self.response['is_sent_receiver'] = is_sent_receiver
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class TicketListHandler(JsonHandler):
    @admin_auth_async
    @parse_argument([('start', int, 0), ('size', int, 10), ('q', str, None),
        ('receive_user_oid', str, None),('company_oid', str, None), ('content_oid', str, None), ('ticket_order_oid', str, None)])
    async def get(self, *args, **kwargs):
        parsed_args = kwargs.get('parsed_args')
        q = {'$and': [{}]}
        if parsed_args['company_oid']:
            q['$and'].append({'company_oid': ObjectId(parsed_args['company_oid'])})
        if parsed_args['content_oid']:
            q['$and'].append({'content_oid': ObjectId(parsed_args['content_oid'])})
        if parsed_args['receive_user_oid']:
            q['$and'].append({'receive_user_oid': ObjectId(parsed_args['receive_user_oid'])})
        if parsed_args['ticket_order_oid']:
            q['$and'].append({'ticket_order_oid': ObjectId(parsed_args['ticket_order_oid'])})
        if parsed_args['q']:
            search_q = {'$or': [
                {'status': {'$regex': parsed_args['q']}},
            ]}
            q['$and'].append(search_q)
        count = await TicketModel.count(query=q)
        result = await TicketModel.find(query=q, skip=parsed_args['start'], limit=parsed_args['size'])
        for res in result:
            res['ticket_order'] = await TicketOrderModel.get_id(res['ticket_order_oid'])
            res.pop('ticket_order_oid')
            res['ticket_type'] = await TicketTypeModel.get_id(res['ticket_type_oid'])
            res.pop('ticket_type_oid')
            res['content'] = await ContentModel.get_id(res['content_oid'])
            res.pop('content_oid')
            if 'send_user_oid' in res:
                res['send_user'] = await UserModel.get_id(res['send_user_oid'])
                res.pop('send_user_oid')
            if 'receive_user_oid' in res:
                res['receive_user'] = await UserModel.get_id(res['receive_user_oid'])
                res.pop('receive_user_oid')
            if 'history_send_user_oids' in res:
                res['history_send_users'] = list()
                for user_oid in res['history_send_user_oids']:
                    user = await UserModel.get_id(user_oid, fields=[('name'), ('mobile_number')])
                    res['history_send_users'].append(user)
                res.pop('history_send_user_oids')
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
        for d in self.json_decoded_body['days']:
            if d['entered']:
                d['entered_at'] = self.json_decoded_body['updated_at']
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
        self.response['data']['ticket_order'] = await TicketOrderModel.get_id(self.response['data']['ticket_order_oid'])
        self.response['data'].pop('ticket_order_oid')
        self.response['data']['ticket_type'] = await TicketTypeModel.get_id(self.response['data']['ticket_type_oid'])
        self.response['data'].pop('ticket_type_oid')
        self.response['data']['content'] = await ContentModel.get_id(self.response['data']['content_oid'])
        self.response['data'].pop('content_oid')
        if 'send_user_oid' in self.response['data']:
            self.response['data']['send_user'] = await UserModel.get_id(self.response['data']['send_user_oid'])
            self.response['data'].pop('send_user_oid')
        if 'receive_user_oid' in self.response['data']:
            self.response['data']['receive_user'] = await UserModel.get_id(self.response['data']['receive_user_oid'])
            self.response['data'].pop('receive_user_oid')
        if 'history_send_user_oids' in self.response['data']:
            self.response['data']['history_send_users'] = list()
            for user_oid in self.response['data']['history_send_user_oids']:
                user = await UserModel.get_id(user_oid, fields=[('name'), ('mobile_number')])
                self.response['data']['history_send_users'].append(user)
            self.response['data'].pop('history_send_user_oids')
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class TicketRegisterUserHandler(JsonHandler):
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
        parsed_args = self.json_decoded_body
        user = await create_user(parsed_args)
        document = {
            '$set': {
                'receive_user_oid': user['_id'],
                'status': TicketModel.Status.register.name
            }
        }
        self.response['data'] = await TicketModel.update(query, document)
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class TicketEnterUserHandler(JsonHandler):
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
        days = self.json_decoded_body['days']
        for d in days:
            if entered:
                d.entered_at = datetime.utcnow()
        document = {
            '$set': {
                'status': TicketModel.Status.use,
                'days': days
            }
        }
        self.response['data'] = await TicketModel.update(query, document)
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class TicketCancelHandler(JsonHandler):
    @admin_auth_async
    async def put(self, *args, **kwargs):
        _id = kwargs.get('_id', None)
        if not _id or len(_id) != 24:
            raise HTTPError(400, 'invalid _id')
        query = {
            '_id': ObjectId(_id)
        }
        document = {
            '$set': {
                'status': TicketModel.Status.cancel.name,
                'updated_at': datetime.utcnow()
            }
        }
        self.response['data'] = await TicketModel.update(query, document)
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()

class TicketOrderSerialNumberList(JsonHandler):
    @admin_auth_async
    @parse_argument([('start', int, 0), ('size', int, 10)])
    async def get(self, *args, **kwargs):
        _id = kwargs.get('_id', None)
        if not _id or len(_id) != 24:
            raise HTTPError(400, 'invalid _id')
        res = await TicketModel.find({'ticket_order_oid': ObjectId(_id)}, fields=[('serial_number')])
        count = await TicketModel.count({'ticket_order_oid': ObjectId(_id)})
        self.response['data'] = res
        self.response['count'] = count
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class TicketSmsSendHandler(JsonHandler):
    @admin_auth_async
    async def put(self, *args, **kwargs):
        _id = kwargs.get('_id', None)
        if not _id or len(_id) != 24:
            raise HTTPError(400, 'invalid _id')
        sms_message = self.json_decoded_body.get('sms_message', None)
        if not sms_message or len(sms_message) == 0:
            raise HTTPError(400, 'invalid sms_message')
        ticket = await TicketModel.find_one({'_id': ObjectId(_id)})
        if not ticket:
            raise HTTPError(400, 'not exist _id')
        user = await UserModel.find_one({'_id': ticket['receive_user_oid']})
        # send SMS
        is_sent_receiver = await send_sms(
            {
                'type': 'unicode',
                'from': 'tkit',
                'to': user['mobile_number'],
                'text': sms_message
            }
        )
        self.response['data'] = ticket
        self.response['is_sent_receiver'] = is_sent_receiver
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class TicketLogListHandler(JsonHandler):
    @admin_auth_async
    @parse_argument([('start', int, 0), ('size', int, 10), ('content_oid', str, None), ('q', str, None)])
    async def get(self, *args, **kwargs):
        q = {}
        parsed_args = kwargs.get('parsed_args')
        if 'content_oid' in parsed_args and parsed_args['content_oid']:
            q = {'$and': [{
                'content_oid': ObjectId(parsed_args['content_oid'])
            }]}
        if 'q' in parsed_args and parsed_args['q']:
            user_q = {'$or': [
                {'name': {'$regex': parsed_args['q']}},
                {'mobile_number': {'$regex': parsed_args['q']}}
            ]}
            users = await UserModel.find(query=user_q)
            if users:
                user_q = {
                    '$or': [
                        {'send_user_oid': { '$in': []}},
                        {'receive_user_oid': { '$in': []}},
                    ]
                }
                for user in users:
                    user_q['$or'][0]['send_user_oid']['$in'].append(user['_id'])
                    user_q['$or'][1]['receive_user_oid']['$in'].append(user['_id'])
            if 'content_oid' in parsed_args and parsed_args['content_oid']:
                q['$and'].append(user_q)
            else:
                q = user_q
        count = await TicketLogModel.count(query=q)
        result = await TicketLogModel.find(query=q, skip=parsed_args['start'], limit=parsed_args['size'])
        for res in result:
            res['send_user'] = await UserModel.get_id(res['send_user_oid'], fields=[('name'), ('mobile_number')])
            res.pop('send_user_oid')
            res['receive_user'] = await UserModel.get_id(res['receive_user_oid'], fields=[('name'), ('mobile_number')])
            res.pop('receive_user_oid')
            res['content'] = await ContentModel.get_id(res['content_oid'], fields=[('name')])
            res.pop('content_oid')
            res['tickets'] = list()
            for oid in res['ticket_oids']:
                tm = await TicketModel.get_id(oid, fields=[('ticket_type_oid')])
                ttm = await TicketTypeModel.get_id(tm['ticket_type_oid'], fields=[('name'), ('desc')])
                ticket = {
                    '_id': tm['_id'],
                    'ticket_type': ttm
                }
                res['tickets'].append(ticket)
            res.pop('ticket_oids')
        self.response['data'] = result
        self.response['count'] = count
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class TicketLogHandler(JsonHandler):
    @admin_auth_async
    async def get(self, *args, **kwargs):
        _id = kwargs.get('_id', None)
        if not _id or len(_id) != 24:
            raise HTTPError(400, 'invalid _id')
        ticket_log = await TicketLogModel.find_one({'_id': ObjectId(_id)})
        if not ticket_log:
            raise HTTPError(400, 'not exist ticket log')
        ticket_log['send_user'] = await UserModel.get_id(ticket_log['send_user_oid'], fields=[('name'), ('mobile_number')])
        ticket_log.pop('send_user_oid')
        ticket_log['receive_user'] = await UserModel.get_id(ticket_log['receive_user_oid'], fields=[('name'), ('mobile_number')])
        ticket_log.pop('receive_user_oid')
        ticket_log['content'] = await ContentModel.get_id(ticket_log['content_oid'], fields=[('name')])
        ticket_log.pop('content_oid')
        ticket_log['tickets'] = list()
        for oid in ticket_log['ticket_oids']:
            tm = await TicketModel.get_id(oid, fields=[('ticket_type_oid'), ('receive_user_oid'), ('status')])
            ttm = await TicketTypeModel.get_id(tm['ticket_type_oid'], fields=[('name'), ('desc')])
            receive_user = await UserModel.get_id(tm['receive_user_oid'], fields=[('name'), ('mobile_number')])
            ticket = {
                '_id': tm['_id'],
                'ticket_type': ttm,
                'receive_user': receive_user,
                'status': tm['status']
            }
            ticket_log['tickets'].append(ticket)
        ticket_log.pop('ticket_oids')
        self.response['data'] = ticket_log
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class TicketEntranceListHandler(JsonHandler):
    @admin_auth_async
    @parse_argument([('start', int, 0), ('size', int, 10),
        ('receive_user_oid', str, None),('company_oid', str, None), ('content_oid', str, None), ('ticket_order_oid', str, None)])
    async def get(self, *args, **kwargs):
        parsed_args = kwargs.get('parsed_args')
        q = {'$and': [{}]}
        if parsed_args['company_oid']:
            q['$and'].append({'company_oid': ObjectId(parsed_args['company_oid'])})
        if parsed_args['content_oid']:
            q['$and'].append({'content_oid': ObjectId(parsed_args['content_oid'])})
        if parsed_args['receive_user_oid']:
            q['$and'].append({'receive_user_oid': ObjectId(parsed_args['receive_user_oid'])})
        if parsed_args['ticket_order_oid']:
            q['$and'].append({'ticket_order_oid': ObjectId(parsed_args['ticket_order_oid'])})
        search_q = {'$or': [
            {'status': TicketModel.Status.send.name},
            {'status': TicketModel.Status.register.name},
            {'status': TicketModel.Status.pay.name},
            {'status': TicketModel.Status.use.name},
            {'status': TicketModel.Status.cancel.name}
        ]}
        q['$and'].append(search_q)
        count = await TicketModel.count(query=q)
        result = await TicketModel.find(query=q, skip=parsed_args['start'], limit=parsed_args['size'])
        for res in result:
            res['ticket_order'] = await TicketOrderModel.get_id(res['ticket_order_oid'])
            res.pop('ticket_order_oid')
            res['ticket_type'] = await TicketTypeModel.get_id(res['ticket_type_oid'])
            res.pop('ticket_type_oid')
            res['content'] = await ContentModel.get_id(res['content_oid'])
            res.pop('content_oid')
            if 'send_user_oid' in res:
                res['send_user'] = await UserModel.get_id(res['send_user_oid'])
                res.pop('send_user_oid')
            if 'receive_user_oid' in res:
                res['receive_user'] = await UserModel.get_id(res['receive_user_oid'])
                res.pop('receive_user_oid')
            if 'history_send_user_oids' in res:
                res['history_send_users'] = list()
                for user_oid in res['history_send_user_oids']:
                    user = await UserModel.get_id(user_oid, fields=[('name'), ('mobile_number')])
                    res['history_send_users'].append(user)
                res.pop('history_send_user_oids')
        self.response['data'] = result
        self.response['count'] = count
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()
