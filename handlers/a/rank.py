# -*- coding: utf-8 -*-

from bson import ObjectId

from tornado.web import HTTPError

from common.decorators import admin_auth_async, parse_argument

from handlers.base import JsonHandler
from models.ticket import TicketModel, TicketOrderModel, TicketTypeModel
from models.content import ContentModel


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
                    "pend": {
                        "$sum": {
                            "$cond": [ { "$eq": [ "$status", "pend" ] }, 1, 0 ]
                        }
                    },
                    "send": {
                        "$sum": {
                            "$cond": [ { "$eq": [ "$status", "send" ] }, 1, 0 ]
                        }
                    },
                    "register": {
                        "$sum": {
                            "$cond": [ { "$eq": [ "$status", "register" ] }, 1, 0 ]
                        }
                    },
                    "pay": {
                        "$sum": {
                            "$cond": [ { "$eq": [ "$status", "pay" ] }, 1, 0 ]
                        }
                    },
                    "use": {
                        "$sum": {
                            "$cond": [ { "$eq": [ "$status", "use" ] }, 1, 0 ]
                        }
                    },
                    "cancel": {
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
            tos['ticket_order'] = await TicketOrderModel.get_id(tos['_id'], fields=[('receiver.name'), ('receiver.mobile_number'), ('ticket_type_oid'), ('content_oid')])
            tos.pop('_id')
            tos['ticket_type'] = await TicketTypeModel.get_id(tos['ticket_order']['ticket_type_oid'], fields=[('name'), ('desc')])
            tos['content'] = await ContentModel.get_id(tos['ticket_order']['content_oid'], fields=[('name')])
        self.response['data'] = ticket_orders_stats
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()
