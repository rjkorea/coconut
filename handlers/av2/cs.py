# -*- coding: utf-8 -*-


from bson import ObjectId

from tornado.web import HTTPError

from common.decorators import admin_auth_async, parse_argument

from handlers.base import JsonHandler
from models.content import ContentModel
from models.ticket import TicketModel, TicketTypeModel
from models.user import UserModel


class TicketListHandler(JsonHandler):
    @admin_auth_async
    @parse_argument([('start', int, 0), ('size', int, 10), ('user_oid', str, None)])
    async def get(self, *args, **kwargs):
        parsed_args = kwargs.get('parsed_args')
        user_oid = parsed_args['user_oid']
        if not user_oid or len(user_oid) != 24:
            raise HTTPError(400, self.set_error(1, 'invalid user_oid'))
        q = {
            '$and': [
                {
                    '$or': [
                        {'status': TicketModel.Status.send.name},
                        {'status': TicketModel.Status.register.name},
                        {'status': TicketModel.Status.pay.name},
                        {'status': TicketModel.Status.use.name},
                        {'status': TicketModel.Status.cancel.name},
                    ]
                },
                {
                    '$or': [
                        {'receive_user_oid': ObjectId(user_oid)},
                        {'history_send_user_oids': ObjectId(user_oid)},
                    ]
                }
            ]
        }
        count = await TicketModel.count(query=q)
        tickets = await TicketModel.find(query=q, skip=parsed_args['start'], limit=parsed_args['size'], sort=[('updated_at', -1)])
        for t in tickets:
            t['content'] = await ContentModel.get_id(t['content_oid'], fields=[('name')])
            t.pop('content_oid')
            t['ticket_type'] = await TicketTypeModel.get_id(t['ticket_type_oid'], fields=[('name'), ('desc'), ('color')])
            t.pop('ticket_type_oid')
            t['receive_user'] = await UserModel.get_id(t['receive_user_oid'], fields=[('last_name'), ('name'), ('mobile')])
            t.pop('receive_user_oid')
        self.response['count'] = count
        self.response['data'] = tickets
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()
