# -*- coding: utf-8 -*-

from bson import ObjectId

from tornado.web import HTTPError

from common import hashers
from common.decorators import user_auth_async, parse_argument

from handlers.base import JsonHandler
from models.user import UserModel
from models.session import UserSessionModel


class UserHandler(JsonHandler):
    @parse_argument([('name', str, None), ('mobile_number', str, None)])
    async def get(self, *args, **kwargs):
        parsed_args = kwargs.get('parsed_args')
        if not parsed_args['name']:
            raise HTTPError(400, 'invalid name')
        if not parsed_args['mobile_number']:
            raise HTTPError(400, 'invalid mobile_number')
        q = {
            'name': parsed_args['name'],
            'mobile_number': parsed_args['mobile_number']
        }
        user = await UserModel.find_one(query=q)
        if not user:
            raise HTTPError(400, 'not exist user')
        res = {
            '_id': user['_id']
        }
        if 'password' in user:
            res['has_password'] = True
        else:
            res['has_password'] = False
        self.response['data'] = res
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class UserNewPasswordHandler(JsonHandler):
    async def put(self, *args, **kwargs):
        user_oid = kwargs.get('_id', None)
        if not user_oid:
            raise HTTPError(400, 'invalid user_oid')
        user = await UserModel.find_one({'_id': ObjectId(user_oid)})
        if not user:
            raise HTTPError(400, 'not exist user')
        if 'password' in user:
            raise HTTPError(400, 'exist password')
        password = self.json_decoded_body.get('password', None)
        if not password or len(password) == 0 or not hashers.validate_user_password(password):
            raise HTTPError(400, 'invalid password')
        password2 = self.json_decoded_body.get('password2', None)
        if not password or len(password) == 0 or not hashers.validate_user_password(password):
            raise HTTPError(400, 'invalid password2')
        if password != password2:
            raise HTTPError(400, 'password and password2 not matched')
        await UserModel.update({'_id': user['_id']}, {'$set': {'password': hashers.make_password(password)}})
        session = UserSessionModel()
        session.data['user_oid'] = user['_id']
        session_oid = await session.insert()
        user['usk'] = str(session_oid)
        self.response['data'] = user
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class UserAuthPasswordHandler(JsonHandler):
    async def put(self, *args, **kwargs):
        user_oid = kwargs.get('_id', None)
        if not user_oid:
            raise HTTPError(400, 'invalid user_oid')
        user = await UserModel.find_one({'_id': ObjectId(user_oid)})
        if not user:
            raise HTTPError(400, 'not exist user')
        if 'password' not in user:
            raise HTTPError(400, 'does not set password')
        password = self.json_decoded_body.get('password', None)
        if not password or len(password) == 0 or not hashers.validate_user_password(password):
            raise HTTPError(400, 'invalid password')
        if not hashers.check_password(password, user['password']):
            raise HTTPError(400, 'invalid password')
        session = UserSessionModel()
        session.data['user_oid'] = user['_id']
        session_oid = await session.insert()
        user['usk'] = str(session_oid)
        self.response['data'] = user
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


# class TicketUnusedListHandler(JsonHandler):
#     @user_auth_async
#     @parse_argument([('start', int, 0), ('size', int, 10), ('content_oid', str, None)])
#     async def get(self, *args, **kwargs):
#         ticket_order_oid = kwargs.get('_id', None)
#         if not ticket_order_oid or len(ticket_order_oid) != 24:
#             raise HTTPError(400, 'invalid ticket_order_oid')
#         parsed_args = kwargs.get('parsed_args')
#         q = {
#             'ticket_order_oid': ObjectId(ticket_order_oid),
#             'status': TicketModel.Status.pend.name,
#             'enabled': True
#         }
#         if parsed_args['content_oid']:
#             q['content_oid'] = ObjectId(parsed_args['content_oid'])
#         count = await TicketModel.count(query=q)
#         result = await TicketModel.find(query=q, skip=parsed_args['start'], limit=parsed_args['size'])
#         for res in result:
#             res['ticket_type'] = await TicketTypeModel.get_id(res['ticket_type_oid'])
#             res.pop('ticket_type_oid')
#             res['ticket_order'] = await TicketOrderModel.get_id(res['ticket_order_oid'])
#             res.pop('ticket_order_oid')
#             res['content'] = await ContentModel.get_id(res['content_oid'])
#             res.pop('content_oid')
#         self.response['data'] = result
#         self.response['count'] = count
#         self.write_json()

#     async def options(self, *args, **kwargs):
#         self.response['message'] = 'OK'
#         self.write_json()


# class TicketUsedListHandler(JsonHandler):
#     @user_auth_async
#     @parse_argument([('start', int, 0), ('size', int, 10), ('content_oid', str, None)])
#     async def get(self, *args, **kwargs):
#         ticket_order_oid = kwargs.get('_id', None)
#         if not ticket_order_oid or len(ticket_order_oid) != 24:
#             raise HTTPError(400, 'invalid ticket_order_oid')
#         parsed_args = kwargs.get('parsed_args')
#         q = {
#             '$and': [
#                 {
#                     'ticket_order_oid': ObjectId(ticket_order_oid),
#                     'enabled': True
#                 },
#                 {
#                     '$or': [
#                         {'status': TicketModel.Status.send.name},
#                         {'status': TicketModel.Status.register.name},
#                         {'status': TicketModel.Status.use.name},
#                         {'status': TicketModel.Status.cancel.name}
#                     ]
#                 }
#             ]
#         }
#         if parsed_args['content_oid']:
#             q['$and'][0]['content_oid'] = ObjectId(parsed_args['content_oid'])
#         count = await TicketModel.count(query=q)
#         result = await TicketModel.find(query=q, skip=parsed_args['start'], limit=parsed_args['size'])
#         for res in result:
#             res['ticket_type'] = await TicketTypeModel.get_id(res['ticket_type_oid'])
#             res.pop('ticket_type_oid')
#             res['ticket_order'] = await TicketOrderModel.get_id(res['ticket_order_oid'])
#             res.pop('ticket_order_oid')
#             res['content'] = await ContentModel.get_id(res['content_oid'])
#             res.pop('content_oid')
#             if 'user_oid'in res:
#                 res['user'] = await UserModel.get_id(res['user_oid'])
#                 res.pop('user_oid')
#         self.response['data'] = result
#         self.response['count'] = count
#         self.write_json()

#     async def options(self, *args, **kwargs):
#         self.response['message'] = 'OK'
#         self.write_json()


# class TicketRegisterHandler(JsonHandler):
#     @user_auth_async
#     async def put(self, *args, **kwargs):
#         _id = kwargs.get('_id', None)
#         if not _id or len(_id) != 24:
#             raise HTTPError(400, 'invalid _id')
#         self.response['_id'] = _id
#         self.response['data'] = self.json_decoded_body
#         self.write_json()

#     async def options(self, *args, **kwargs):
#         self.response['message'] = 'OK'
#         self.write_json()


# class TicketCancelHandler(JsonHandler):
#     @user_auth_async
#     async def put(self, *args, **kwargs):
#         _id = kwargs.get('_id', None)
#         if not _id or len(_id) != 24:
#             raise HTTPError(400, 'invalid _id')
#         self.response['_id'] = _id
#         self.response['data'] = self.json_decoded_body
#         self.write_json()

#     async def options(self, *args, **kwargs):
#         self.response['message'] = 'OK'
#         self.write_json()


# class TicketSendHandler(JsonHandler):
#     @user_auth_async
#     async def put(self, *args, **kwargs):
#         self.response['data'] = self.json_decoded_body
#         self.write_json()

#     async def options(self, *args, **kwargs):
#         self.response['message'] = 'OK'
#         self.write_json()


# class TicketSendBatchHandler(JsonHandler):
#     @user_auth_async
#     async def put(self, *args, **kwargs):
#         self.response['data'] = 'batch'
#         self.write_json()

#     async def options(self, *args, **kwargs):
#         self.response['message'] = 'OK'
#         self.write_json()


# class TicketListMeHandler(JsonHandler):
#     @user_auth_async
#     @parse_argument([('start', int, 0), ('size', int, 10), ('content_oid', str, None)])
#     async def get(self, *args, **kwargs):
#         parsed_args = kwargs.get('parsed_args')
#         q = {
#             '$and': [
#                 {
#                     'receive_user_oid': self.current_user['_id'],
#                     'enabled': True
#                 },
#                 {
#                     '$or': [
#                         {'status': TicketModel.Status.register.name},
#                         {'status': TicketModel.Status.use.name},
#                         {'status': TicketModel.Status.cancel.name}
#                     ]
#                 }
#             ]
#         }
#         if parsed_args['content_oid']:
#             q['$and'][0]['content_oid'] = ObjectId(parsed_args['content_oid'])
#         count = await TicketModel.count(query=q)
#         result = await TicketModel.find(query=q, skip=parsed_args['start'], limit=parsed_args['size'])
#         for res in result:
#             res['ticket_type'] = await TicketTypeModel.get_id(res['ticket_type_oid'])
#             res.pop('ticket_type_oid')
#             res['ticket_order'] = await TicketOrderModel.get_id(res['ticket_order_oid'])
#             res.pop('ticket_order_oid')
#             res['content'] = await ContentModel.get_id(res['content_oid'])
#             res.pop('content_oid')
#             if 'send_user_oid'in res:
#                 res['send_user'] = await UserModel.get_id(res['send_user_oid'])
#                 res.pop('send_user_oid')
#             if 'receive_user_oid'in res:
#                 res['receive_user'] = await UserModel.get_id(res['receive_user_oid'])
#                 res.pop('receive_user_oid')
#         self.response['data'] = result
#         self.response['count'] = count
#         self.write_json()

#     async def options(self, *args, **kwargs):
#         self.response['message'] = 'OK'
#         self.write_json()


# class TicketListHandler(JsonHandler):
#     @user_auth_async
#     @parse_argument([('start', int, 0), ('size', int, 10), ('content_oid', str, None)])
#     async def get(self, *args, **kwargs):
#         parsed_args = kwargs.get('parsed_args')
#         q = {
#             '$and': [
#                 {
#                     'receive_user_oid': self.current_user['_id'],
#                     'enabled': True
#                 },
#                 {
#                     '$or': [
#                         {'status': TicketModel.Status.send.name},
#                         {'status': TicketModel.Status.register.name},
#                         {'status': TicketModel.Status.use.name},
#                         {'status': TicketModel.Status.cancel.name}
#                     ]
#                 }
#             ]
#         }
#         if parsed_args['content_oid']:
#             q['$and'][0]['content_oid'] = ObjectId(parsed_args['content_oid'])
#         count = await TicketModel.count(query=q)
#         result = await TicketModel.find(query=q, skip=parsed_args['start'], limit=parsed_args['size'])
#         for res in result:
#             res['ticket_type'] = await TicketTypeModel.get_id(res['ticket_type_oid'])
#             res.pop('ticket_type_oid')
#             res['ticket_order'] = await TicketOrderModel.get_id(res['ticket_order_oid'])
#             res.pop('ticket_order_oid')
#             res['content'] = await ContentModel.get_id(res['content_oid'])
#             res.pop('content_oid')
#             if 'send_user_oid'in res:
#                 res['send_user'] = await UserModel.get_id(res['send_user_oid'])
#                 res.pop('send_user_oid')
#             if 'receive_user_oid'in res:
#                 res['receive_user'] = await UserModel.get_id(res['receive_user_oid'])
#                 res.pop('receive_user_oid')
#         self.response['data'] = result
#         self.response['count'] = count
#         self.write_json()

#     async def options(self, *args, **kwargs):
#         self.response['message'] = 'OK'
#         self.write_json()
