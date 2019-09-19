# -*- coding: utf-8 -*-


from bson import ObjectId

from tornado.web import HTTPError

from common.decorators import admin_auth_async, parse_argument

from handlers.base import JsonHandler
from models.ticket import TicketModel, TicketTypeModel, TicketOrderModel
from models.user import UserModel


class SellerStatsListHandler(JsonHandler):
    @admin_auth_async
    @parse_argument([('start', int, 0), ('size', int, 10), ('content_oid', str, None)])
    async def get(self, *args, **kwargs):
        parsed_args = kwargs.get('parsed_args')
        content_oid = parsed_args['content_oid']
        if not content_oid or len(content_oid) != 24:
            raise HTTPError(400, self.set_error(1, 'invalid content_oid'))
        pipeline = [
            {
                '$match': {
                    'content_oid': ObjectId(content_oid),
                    'commission': {
                        '$exists': True
                    },
                    'enabled': True
                }
            },
            {
                '$group': {
                    '_id': {
                        'user_oid': '$user_oid'
                    },
                    'ticket_orders': {
                        '$push': {
                            '_id': '$_id',
                            'commission': '$commission',
                            'ticket_type_oid': '$ticket_type_oid',
                            'type': '$type'
                        }
                    }
                }
            },
            {
                '$skip': parsed_args['start']
            },
            {
                '$limit': parsed_args['size']
            }
        ]
        seller_stats_list = await TicketOrderModel.aggregate(pipeline, parsed_args['size'])
        for s in seller_stats_list:
            s['user'] = await UserModel.get_id(s['_id']['user_oid'], fields=[('name'), ('mobile'), ('memo')])
            s.pop('_id')
            for to in s['ticket_orders']:
                to['ticket_type'] = await TicketTypeModel.get_id(to['ticket_type_oid'], fields=[('name'), ('desc')])
                to.pop('ticket_type_oid')
                to['ticket_used_count'] = await TicketModel.count({'ticket_order_oid': to['_id'], 'status': 'use'})
                to.pop('_id')
        self.response['data'] = seller_stats_list
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()
