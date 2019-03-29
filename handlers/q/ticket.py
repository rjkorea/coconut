# -*- coding: utf-8 -*-

from datetime import datetime
from bson import ObjectId

from tornado.web import HTTPError

from common.decorators import admin_auth_async, parse_argument

from handlers.base import JsonHandler
from models.ticket import TicketModel, TicketTypeModel
from models.user import UserModel
from models.content import ContentModel


class TicketListUserHandler(JsonHandler):
    @admin_auth_async
    @parse_argument([('user_oid', str, None), ('start', int, 0), ('size', int, 10)])
    async def get(self, *args, **kwargs):
        content_oid = kwargs.get('_id', None)
        if not content_oid or len(content_oid) != 24:
            raise HTTPError(400, 'invalid content_oid ')
        parsed_args = kwargs.get('parsed_args')
        if not parsed_args['user_oid'] or len(parsed_args['user_oid']) != 24:
            raise HTTPError(400, 'invalid user_oid ')
        user = await UserModel.find_one({'_id': ObjectId(parsed_args['user_oid'])})
        if not user:
            raise HTTPError(400, 'no exist user')
        q = {
            '$and': [
                {'content_oid': ObjectId(content_oid)},
                {'receive_user_oid': ObjectId(parsed_args['user_oid'])},
                {'enabled': True},
                {'$or': [
                    {'status': TicketModel.Status.register.name},
                    {'status': TicketModel.Status.pay.name},
                    {'status': TicketModel.Status.use.name},
                    {'status': TicketModel.Status.cancel.name}
                ]}
            ]
        }
        count = await TicketModel.count(q)
        tickets = await TicketModel.find(query=q, fields={'content_oid': True, 'ticket_type_oid': True, 'status': True, 'price': True}, skip=parsed_args['start'], limit=parsed_args['size'])
        for t in tickets:
            tt = await TicketTypeModel.get_id(t['ticket_type_oid'], fields={'_id': False, 'name': True, 'desc': True})
            t['ticket_type'] = tt
            c = await ContentModel.get_id(t['content_oid'], fields={'_id': False, 'name': True})
            t['content'] = c
        self.response['count'] = count
        self.response['data'] = tickets
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
            raise HTTPError(400, 'not exist ticket')
        query = {
            '_id': ObjectId(_id)
        }
        document = {
            '$set': {
                'status': TicketModel.Status.use.name,
                'updated_at': datetime.utcnow()
            }
        }
        self.response['data'] = await TicketModel.update(query, document)
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()