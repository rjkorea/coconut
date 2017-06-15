# -*- coding: utf-8 -*-

from bson import ObjectId

from tornado.web import HTTPError

from common import hashers
from common.decorators import user_auth_async, parse_argument

from handlers.base import JsonHandler
from models.user import UserModel
from models.content import ContentModel
from models.ticket import TicketOrderModel, TicketTypeModel, TicketModel

from models import create_user


class TicketOrderListHandler(JsonHandler):
    @user_auth_async
    @parse_argument([('start', int, 0), ('size', int, 10), ('content_oid', str, None)])
    async def get(self, *args, **kwargs):
        parsed_args = kwargs.get('parsed_args')
        q = {
            'user_oid': self.current_user['_id']
        }
        if parsed_args['content_oid']:
            q['content_oid'] = ObjectId(parsed_args['content_oid'])
        count = await TicketOrderModel.count(query=q)
        result = await TicketOrderModel.find(query=q, skip=parsed_args['start'], limit=parsed_args['size'])
        for res in result:
            res['ticket_type'] = await TicketTypeModel.get_id(res['ticket_type_oid'])
            res.pop('ticket_type_oid')
        self.response['data'] = result
        self.response['count'] = count
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class TicketUnusedListHandler(JsonHandler):
    @user_auth_async
    @parse_argument([('start', int, 0), ('size', int, 10), ('content_oid', str, None)])
    async def get(self, *args, **kwargs):
        ticket_order_oid = kwargs.get('_id', None)
        if not ticket_order_oid or len(ticket_order_oid) != 24:
            raise HTTPError(400, 'invalid ticket_order_oid')
        parsed_args = kwargs.get('parsed_args')
        q = {
            'ticket_order_oid': ObjectId(ticket_order_oid),
            'status': TicketModel.Status.pend.name,
            'enabled': True
        }
        if parsed_args['content_oid']:
            q['content_oid'] = ObjectId(parsed_args['content_oid'])
        count = await TicketModel.count(query=q)
        result = await TicketModel.find(query=q, skip=parsed_args['start'], limit=parsed_args['size'])
        for res in result:
            res['ticket_type'] = await TicketTypeModel.get_id(res['ticket_type_oid'])
            res.pop('ticket_type_oid')
            res['ticket_order'] = await TicketOrderModel.get_id(res['ticket_order_oid'])
            res.pop('ticket_order_oid')
            res['content'] = await ContentModel.get_id(res['content_oid'])
            res.pop('content_oid')
        self.response['data'] = result
        self.response['count'] = count
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class TicketUsedListHandler(JsonHandler):
    @user_auth_async
    @parse_argument([('start', int, 0), ('size', int, 10), ('content_oid', str, None)])
    async def get(self, *args, **kwargs):
        ticket_order_oid = kwargs.get('_id', None)
        if not ticket_order_oid or len(ticket_order_oid) != 24:
            raise HTTPError(400, 'invalid ticket_order_oid')
        parsed_args = kwargs.get('parsed_args')
        q = {
            '$and': [
                {
                    'ticket_order_oid': ObjectId(ticket_order_oid),
                    'enabled': True
                },
                {
                    '$or': [
                        {'status': TicketModel.Status.send.name},
                        {'status': TicketModel.Status.register.name},
                        {'status': TicketModel.Status.use.name},
                        {'status': TicketModel.Status.cancel.name}
                    ]
                }
            ]
        }
        if parsed_args['content_oid']:
            q['$and'][0]['content_oid'] = ObjectId(parsed_args['content_oid'])
        count = await TicketModel.count(query=q)
        result = await TicketModel.find(query=q, skip=parsed_args['start'], limit=parsed_args['size'])
        for res in result:
            res['ticket_type'] = await TicketTypeModel.get_id(res['ticket_type_oid'])
            res.pop('ticket_type_oid')
            res['ticket_order'] = await TicketOrderModel.get_id(res['ticket_order_oid'])
            res.pop('ticket_order_oid')
            res['content'] = await ContentModel.get_id(res['content_oid'])
            res.pop('content_oid')
            if 'user_oid'in res:
                res['user'] = await UserModel.get_id(res['user_oid'])
                res.pop('user_oid')
        self.response['data'] = result
        self.response['count'] = count
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class TicketRegisterHandler(JsonHandler):
    @user_auth_async        
    async def put(self, *args, **kwargs):
        _id = kwargs.get('_id', None)
        if not _id or len(_id) != 24:
            raise HTTPError(400, 'invalid _id')
        ticket = await TicketModel.find_one({'_id': ObjectId(_id)})
        if not ticket:
            raise HTTPError(400, 'not exist ticket')
        if ticket['status'] == TicketModel.Status.register.name and 'receive_user_oid' in ticket:
            raise HTTPError(400, 'registerd ticket')

        email = self.json_decoded_body.get('email', None)
        birthday = self.json_decoded_body.get('birthday', None)
        gender = self.json_decoded_body.get('gender', None)
        if email and birthday and gender:
            user = await UserModel.update({'_id': self.current_user['_id']}, {'$set': {'email': email, 'birthday': birthday, 'gender': gender}})
        query = {
            '_id': ObjectId(_id)
        }
        document = {
            '$set': {
                'receive_user_oid': self.current_user['_id'],
                'status': TicketModel.Status.register.name
            }
        }
        self.response['data'] = await TicketModel.update(query, document)
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class TicketCancelHandler(JsonHandler):
    @user_auth_async
    async def put(self, *args, **kwargs):
        _id = kwargs.get('_id', None)
        if not _id or len(_id) != 24:
            raise HTTPError(400, 'invalid _id')
        self.response['_id'] = _id
        self.response['data'] = self.json_decoded_body
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class TicketSendHandler(JsonHandler):
    @user_auth_async
    async def put(self, *args, **kwargs):
        ticket_oids = self.json_decoded_body.get('ticket_oids', None)
        if not ticket_oids or not isinstance(ticket_oids, list):
            raise HTTPError(400, 'invalid ticket_oids')
        receive_user = self.json_decoded_body.get('receive_user', None)
        if not receive_user or not isinstance(receive_user, dict):
            raise HTTPError(400, 'invalid receive_user')
        receive_user = await create_user(receive_user)
        if self.current_user['_id'] == receive_user['_id']:
            raise HTTPError(400, 'cannot send to myself')
        query = {'$or': []}
        for t_oid in ticket_oids:
            query['$or'].append({'_id': ObjectId(t_oid)})
        document = {
            '$set': {
                'status': TicketModel.Status.send.name,
                'send_user_oid': self.current_user['_id'],
                'receive_user_oid': receive_user['_id']
            }
        }
        self.response['data'] = await TicketModel.update(query, document, False, True)
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class TicketSendBatchHandler(JsonHandler):
    @user_auth_async
    async def put(self, *args, **kwargs):
        self.response['data'] = 'batch'
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class TicketListMeHandler(JsonHandler):
    @user_auth_async
    @parse_argument([('start', int, 0), ('size', int, 10), ('content_oid', str, None)])
    async def get(self, *args, **kwargs):
        parsed_args = kwargs.get('parsed_args')
        q = {
            '$and': [
                {
                    'receive_user_oid': self.current_user['_id'],
                    'enabled': True
                },
                {
                    '$or': [
                        {'status': TicketModel.Status.register.name},
                        {'status': TicketModel.Status.use.name},
                        {'status': TicketModel.Status.cancel.name}
                    ]
                }
            ]
        }
        if parsed_args['content_oid']:
            q['$and'][0]['content_oid'] = ObjectId(parsed_args['content_oid'])
        count = await TicketModel.count(query=q)
        result = await TicketModel.find(query=q, skip=parsed_args['start'], limit=parsed_args['size'])
        for res in result:
            res['ticket_type'] = await TicketTypeModel.get_id(res['ticket_type_oid'])
            res.pop('ticket_type_oid')
            res['ticket_order'] = await TicketOrderModel.get_id(res['ticket_order_oid'])
            res.pop('ticket_order_oid')
            res['content'] = await ContentModel.get_id(res['content_oid'])
            res.pop('content_oid')
            if 'send_user_oid'in res:
                res['send_user'] = await UserModel.get_id(res['send_user_oid'])
                res.pop('send_user_oid')
            if 'receive_user_oid'in res:
                res['receive_user'] = await UserModel.get_id(res['receive_user_oid'])
                res.pop('receive_user_oid')
        self.response['data'] = result
        self.response['count'] = count
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class TicketListHandler(JsonHandler):
    @user_auth_async
    @parse_argument([('start', int, 0), ('size', int, 10), ('content_oid', str, None)])
    async def get(self, *args, **kwargs):
        parsed_args = kwargs.get('parsed_args')
        q = {
            '$and': [
                {
                    'receive_user_oid': self.current_user['_id'],
                    'enabled': True
                },
                {
                    '$or': [
                        {'status': TicketModel.Status.send.name},
                        {'status': TicketModel.Status.register.name},
                        {'status': TicketModel.Status.use.name},
                        {'status': TicketModel.Status.cancel.name}
                    ]
                }
            ]
        }
        if parsed_args['content_oid']:
            q['$and'][0]['content_oid'] = ObjectId(parsed_args['content_oid'])
        count = await TicketModel.count(query=q)
        result = await TicketModel.find(query=q, skip=parsed_args['start'], limit=parsed_args['size'])
        for res in result:
            res['ticket_type'] = await TicketTypeModel.get_id(res['ticket_type_oid'])
            res.pop('ticket_type_oid')
            res['ticket_order'] = await TicketOrderModel.get_id(res['ticket_order_oid'])
            res.pop('ticket_order_oid')
            res['content'] = await ContentModel.get_id(res['content_oid'])
            res.pop('content_oid')
            if 'send_user_oid'in res:
                res['send_user'] = await UserModel.get_id(res['send_user_oid'])
                res.pop('send_user_oid')
            if 'receive_user_oid'in res:
                res['receive_user'] = await UserModel.get_id(res['receive_user_oid'])
                res.pop('receive_user_oid')
        self.response['data'] = result
        self.response['count'] = count
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()
