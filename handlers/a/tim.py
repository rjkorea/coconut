# -*- coding: utf-8 -*-

from bson import ObjectId

from tornado.web import HTTPError

from common.decorators import admin_auth_async, parse_argument

from handlers.base import JsonHandler
from models.ticket import TicketModel, TicketOrderModel, TicketTypeModel, TicketLogModel
from models.content import ContentModel


class MatrixTicketOrderHandler(JsonHandler):
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


class MatrixTicketTypeHandler(JsonHandler):
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
                    '_id': '$ticket_type_oid',
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
        ticket_types_stats = await TicketModel.aggregate(pipeline, parsed_args['size'])
        for tts in ticket_types_stats:
            tts['ticket_type'] = await TicketTypeModel.get_id(tts['_id'], fields=[('name'), ('desc')])
            tts.pop('_id')
        self.response['data'] = ticket_types_stats
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class ReportHandler(JsonHandler):
    @admin_auth_async
    async def get(self, *args, **kwargs):
        content_oid = kwargs.get('_id', None)
        if not content_oid or len(content_oid) != 24:
            raise HTTPError(400, 'invalid content_oid')
        self.response['data'] = {
            'total_visit': 0,
            'total_forward': 0,
            'revenue': {
                'cash': 0,
                'creditcard': 0
            },
            'commission': 0.07
        }
        q = {
            'content_oid': ObjectId(content_oid),
            'enabled': True,
            'status': TicketModel.Status.use.name
        }
        self.response['data']['total_visit'] = await TicketModel.count(query=q)
        q = {
            'content_oid': ObjectId(content_oid),
            'action': TicketLogModel.Status.send.name
        }
        self.response['data']['total_forward'] = await TicketLogModel.count(query=q)
        #user aggregate for revenue
        pipeline = [
            {
                '$match': {
                    'content_oid': ObjectId(content_oid),
                    'enabled': True,
                    'status': TicketModel.Status.use.name
                }
            },
            {
                '$unwind': {'path': '$days'}
            },
            {
                '$group': {
                    '_id': '$days.fee.method',
                    'revenue': {
                        '$sum': '$days.fee.price'
                    }
                }
            }
        ]
        aggs = await TicketModel.aggregate(pipeline, 5)
        for a in aggs:
            self.response['data']['revenue'][a['_id']] = a['revenue']
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class AnalyticsHandler(JsonHandler):
    @admin_auth_async
    async def get(self, *args, **kwargs):
        content_oid = kwargs.get('_id', None)
        if not content_oid or len(content_oid) != 24:
            raise HTTPError(400, 'invalid content_oid')
        self.response['data'] = {
            'total_forward': 0,
            'ticket_count': {
                'pend': 0,
                'send': 0,
                'register': 0,
                'pay': 0,
                'use': 0,
                'cancel': 0
            },
            'revenue': 0,
            'gender': {}
        }
        query = {
            'content_oid': ObjectId(content_oid),
            'enabled': True
        }
        # aggregate count for ticket
        pipeline = [
            {
                '$match': {
                    'content_oid': ObjectId(content_oid)
                }
            },
            {
                '$group': {
                    '_id': '$status',
                    'cnt': {
                        '$sum': 1
                    }
                }
            }
        ]
        aggs = await TicketModel.aggregate(pipeline, 10)
        for a in aggs:
            self.response['data']['ticket_count'][a['_id']] = a['cnt']
        # aggregate count for gender
        pipeline = [
            {
                '$match': {
                    '$and': [
                        {'content_oid': ObjectId(content_oid)},
                        {
                            '$or': [
                                {'status': TicketModel.Status.register.name},
                                {'status': TicketModel.Status.pay.name},
                                {'status': TicketModel.Status.use.name}
                            ]
                        }
                    ]
                }
            },
            {
                '$lookup': {
                    'from': 'user',
                    'localField': 'receive_user_oid',
                    'foreignField': '_id',
                    'as': 'receive_user'
                }
            },
            {
                '$group': {
                    '_id': '$receive_user.gender',
                    'count': {
                        '$sum': 1
                    }
                }
            }
        ]
        aggs = await TicketModel.aggregate(pipeline, 10)
        for a in aggs:
            if a['_id']:
                self.response['data']['gender'][a['_id'][0]] = a['count']
        #user aggregate for revenue
        pipeline = [
            {
                '$match': {
                    'content_oid': ObjectId(content_oid),
                    'enabled': True,
                    'status': TicketModel.Status.use.name
                }
            },
            {
                '$group': {
                    '_id': '$days.fee.method',
                    'revenue': {
                        '$sum': '$price'
                    }
                }
            }
        ]
        aggs = await TicketModel.aggregate(pipeline, 5)
        if aggs:
            self.response['data']['revenue'] = aggs[0]['revenue']
        q = {
            'content_oid': ObjectId(content_oid),
            'action': TicketLogModel.Status.send.name
        }
        self.response['data']['total_forward'] = await TicketLogModel.count(query=q)
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()
