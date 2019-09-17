# -*- coding: utf-8 -*-

from bson import ObjectId
from datetime import datetime

from tornado.web import HTTPError

from common.decorators import user_auth_async, parse_argument

from handlers.base import JsonHandler, MultipartFormdataHandler

from models.user import UserModel
from models.content import ContentModel
from models.ticket import TicketOrderModel, TicketTypeModel, TicketModel


class SellerMeHandler(JsonHandler):
    @user_auth_async
    async def get(self, *args, **kwargs):
        user = await UserModel.find_one({'_id': self.current_user['_id']}, fields=[('name'), ('mobile'), ('email'), ('bank'), ('resident_registration_number')])
        if not user:
            raise HTTPError(400, 'not exist user')
        self.response['data'] = user
        self.write_json()

    @user_auth_async
    async def put(self, *args, **kwargs):
        set_doc = {
            'updated_at': datetime.utcnow()
        }
        name = self.json_decoded_body.get('name', None)
        if name.strip() and len(name.strip()) > 0:
            set_doc['name'] = name.strip()
        email = self.json_decoded_body.get('email', None)
        if email.strip() and len(email.strip()) > 0:
            set_doc['email'] = email.strip()
        bank = self.json_decoded_body.get('bank', None)
        if bank and isinstance(bank, dict):
            set_doc['bank'] = bank
        resident_registration_number = self.json_decoded_body.get('resident_registration_number', None)
        if resident_registration_number.strip() and len(resident_registration_number.strip()) > 0:
            set_doc['resident_registration_number'] = resident_registration_number.strip()
        query = {
            '_id': self.current_user['_id']
        }
        document = {
            '$set': set_doc
        }
        await UserModel.update(query, document, False, False)
        self.response['data'] = 'OK'
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class SellerMeCountHandler(JsonHandler):
    @user_auth_async
    @parse_argument([('content_oid', str, None)])
    async def get(self, *args, **kwargs):
        parsed_args = kwargs.get('parsed_args')
        if not parsed_args['content_oid']:
            raise HTTPError(400, 'invalid content_oid')
        q = {
            'content_oid': ObjectId(parsed_args['content_oid']),
            'user_oid': self.current_user['_id'],
            'commission': {
                '$exists': True
            },
            'enabled': True
        }
        self.response['count'] = await TicketOrderModel.count(query=q)
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class SellerTicketListHandler(JsonHandler):
    @user_auth_async
    @parse_argument([('content_oid', str, None), ('start', int, 0), ('size', int, 10)])
    async def get(self, *args, **kwargs):
        parsed_args = kwargs.get('parsed_args')
        if not parsed_args['content_oid']:
            raise HTTPError(400, 'invalid content_oid')
        q = {
            'type': 'network',
            'content_oid': ObjectId(parsed_args['content_oid']),
            'user_oid': self.current_user['_id'],
            'commission': {
                '$exists': True
            },
            'enabled': True
        }
        ticket_orders = await TicketOrderModel.find(query=q, skip=parsed_args['start'], limit=parsed_args['size'], sort=[('created_at', -1)], fields=[('ticket_type_oid'), ('qty'), ('commission')])
        for to in ticket_orders:
            ticket_type = await TicketTypeModel.get_id(to['ticket_type_oid'], fields=[('name')])
            to['ticket_type_name'] = ticket_type['name']
            to.pop('ticket_type_oid')
            to['used_count'] = await TicketModel.count({'ticket_order_oid': to['_id'], 'status': 'use'})
        self.response['data'] = ticket_orders
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class SellerCouponListHandler(JsonHandler):
    @user_auth_async
    @parse_argument([('content_oid', str, None), ('start', int, 0), ('size', int, 10)])
    async def get(self, *args, **kwargs):
        parsed_args = kwargs.get('parsed_args')
        if not parsed_args['content_oid']:
            raise HTTPError(400, 'invalid content_oid')
        q = {
            'type': 'coupon',
            'content_oid': ObjectId(parsed_args['content_oid']),
            'user_oid': self.current_user['_id'],
            'commission': {
                '$exists': True
            },
            'enabled': True
        }
        ticket_orders = await TicketOrderModel.find(query=q, skip=parsed_args['start'], limit=parsed_args['size'], sort=[('created_at', -1)], fields=[('ticket_type_oid'), ('qty'), ('commission')])
        for to in ticket_orders:
            ticket_type = await TicketTypeModel.get_id(to['ticket_type_oid'], fields=[('name')])
            to['ticket_type_name'] = ticket_type['name']
            to.pop('ticket_type_oid')
            to['used_count'] = await TicketModel.count({'ticket_order_oid': to['_id'], 'status': 'use'})
        self.response['data'] = ticket_orders
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class SellerMeContentListHandler(JsonHandler):
    @user_auth_async
    @parse_argument([('start', int, 0), ('size', int, 10)])
    async def get(self, *args, **kwargs):
        parsed_args = kwargs.get('parsed_args')
        pipeline = [
            {
                '$match': {
                    'user_oid': self.current_user['_id'],
                    'commission': {
                        '$exists': True
                    },
                    'enabled': True
                }
            },
            {
                '$group': {
                    '_id': {
                        'content_oid': '$content_oid'
                    }
                }
            }
        ]
        aggs = await TicketOrderModel.aggregate(pipeline, 100)
        contents = list()
        for a in aggs:
            content = await ContentModel.get_id(a['_id']['content_oid'], fields=[('name')])
            contents.append(content)
        self.response['data'] = contents
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class SellerUsedTicketListHandler(JsonHandler):
    @user_auth_async
    @parse_argument([('start', int, 0), ('size', int, 10), ('ticket_order_oid', str, None)])
    async def get(self, *args, **kwargs):
        parsed_args = kwargs.get('parsed_args')
        q = {
            'ticket_order_oid': ObjectId(parsed_args['ticket_order_oid']),
            'status': TicketModel.Status.use.name
        }
        count = await TicketModel.count(query=q)
        result = await TicketModel.find(query=q, skip=parsed_args['start'], limit=parsed_args['size'], fields=[('updated_at'), ('receive_user_oid')])
        for res in result:
            if 'receive_user_oid' in res:
                res['receive_user'] = await UserModel.get_id(res['receive_user_oid'], fields=[('name'), ('mobile'), ('image')])
                res.pop('receive_user_oid')
        self.response['data'] = result
        self.response['count'] = count
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class SellerTicketHistoryListHandler(JsonHandler):
    @user_auth_async
    async def get(self, *args, **kwargs):
        _id = kwargs.get('_id', None)
        ticket = await TicketModel.get_id(ObjectId(_id), fields=[('history_send_user_oids')])
        histories = []
        if 'history_send_user_oids' in ticket:
            for send_user_oid in ticket['history_send_user_oids']:
                send_user = await UserModel.get_id(send_user_oid, fields=[('name'), ('mobile')])
                histories.append(send_user)
        self.response['data'] = histories[::-1]
        self.response['count'] = len(histories)
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()
