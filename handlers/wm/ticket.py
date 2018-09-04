# -*- coding: utf-8 -*-

from datetime import datetime
from bson import ObjectId

from tornado.web import HTTPError

from common.decorators import user_auth_async, parse_argument

from handlers.base import JsonHandler
from models.ticket import TicketTypeModel, TicketOrderModel, TicketModel
from models.content import ContentModel


class TicketOrderListHandler(JsonHandler):
    @user_auth_async
    @parse_argument([('start', int, 0), ('size', int, 10)])
    async def get(self, *args, **kwargs):
        _id = kwargs.get('_id', None)
        if not _id or (len(_id) != 24 and len(_id) != 7):
            raise HTTPError(400, 'invalid _id (user _id or short_id field of content)')
        parsed_args = kwargs.get('parsed_args')
        q = {
            'content_oid': ObjectId(_id),
            'type': 'general',
            'enabled': True
        }
        count = await TicketOrderModel.count(q)
        ticket_orders = await TicketOrderModel.find(query=q, skip=parsed_args['start'], limit=parsed_args['size'])
        result = list()
        for to in ticket_orders:
            tt = await TicketTypeModel.get_id(to['ticket_type_oid'])
            doc = {
                '_id': to['_id'],
                'name': tt['name'],
                'desc': tt['desc'],
                'qty': to['qty']
            }
            if 'fee' in to:
                doc['price'] = to['fee']['price']
            doc['pend'] = await TicketModel.count({'ticket_type_oid': to['ticket_type_oid'], 'status': TicketModel.Status.pend.name})
            result.append(doc)
        self.response['count'] = count
        self.response['data'] = result
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class TicketSendHandler(JsonHandler):
    @user_auth_async
    async def put(self, *args, **kwargs):
        ticket_orders = self.json_decoded_body.get('ticket_orders', None)
        if not ticket_orders or len(ticket_orders) == 0:
            raise HTTPError(400, 'invalid ticket_orders')
        now = datetime.utcnow()
        for to in ticket_orders:
            t_cnt = await TicketModel.count({'ticket_order_oid': ObjectId(to['_id']), 'status': TicketModel.Status.pend.name})
            if t_cnt < to['qty']:
                raise HTTPError(400, 'can\'t buy ticket (ticket_order_oid: %s)' % to['_id'])
            tickets = await TicketModel.find({'ticket_order_oid': ObjectId(to['_id']), 'status': TicketModel.Status.pend.name})
            for i in range(to['qty']):
                q = {'_id': tickets[i]['_id'], 'status': TicketModel.Status.pend.name}
                doc = {
                    '$set': {
                        'receive_user_oid': self.current_user['_id'],
                        'status': TicketModel.Status.send.name,
                        'updated_at': now
                    }
                }
                res = await TicketModel.update(q, doc, False, False)
        self.response['data'] = 'OK'
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()
