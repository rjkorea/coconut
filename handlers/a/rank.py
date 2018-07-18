# -*- coding: utf-8 -*-

from bson import ObjectId

from tornado.web import HTTPError

from common.decorators import admin_auth_async, parse_argument

from handlers.base import JsonHandler
from models.ticket import TicketModel, TicketOrderModel


class RankHandler(JsonHandler):
    @admin_auth_async
    @parse_argument([('start', int, 0), ('size', int, 10), ('sort', str, 'register_count')])
    async def get(self, *args, **kwargs):
        parsed_args = kwargs.get('parsed_args')
        content_oid = kwargs.get('_id', None)
        if not content_oid or len(content_oid) != 24:
            raise HTTPError(400, 'invalid content_oid')
        pipeline = [
            {
                '$match': {'content_oid': ObjectId(content_oid)}
            },
            {
                '$group': {
                    '_id': '$ticket_order_oid',
                    "send_count": {
                        "$sum": {
                            "$cond": [ { "$eq": [ "$status", "send" ] }, 1, 0 ]
                        }
                    },
                    "register_count": {
                        "$sum": {
                            "$cond": [ { "$eq": [ "$status", "register" ] }, 1, 0 ]
                        }
                    },
                    "pay_count": {
                        "$sum": {
                            "$cond": [ { "$eq": [ "$status", "pay" ] }, 1, 0 ]
                        }
                    },
                    "use_count": {
                        "$sum": {
                            "$cond": [ { "$eq": [ "$status", "use" ] }, 1, 0 ]
                        }
                    },
                    "cancel_count": {
                        "$sum": {
                            "$cond": [ { "$eq": [ "$status", "cancel" ] }, 1, 0 ]
                        }
                    }
                }
            },
            {
                '$sort': {
                    parsed_args['sort']: -1
                }
            },
            {
                '$skip': parsed_args['start']
            },
            {
                '$limit': parsed_args['size']
            }
        ]
        ticket_orders_stats = await TicketModel.aggregate(pipeline, parsed_args['size'])
        for tos in ticket_orders_stats:
            tos['ticket_order'] = await TicketOrderModel.get_id(tos['_id'], fields=[('receiver.name'), ('receiver.mobile_number')])
            tos.pop('_id')
        self.response['data'] = ticket_orders_stats
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()
