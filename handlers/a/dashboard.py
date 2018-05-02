# -*- coding: utf-8 -*-

from bson import ObjectId

from tornado.web import HTTPError

from common.decorators import admin_auth_async

from handlers.base import JsonHandler
from models.company import CompanyModel
from models.user import UserModel
from models.content import ContentModel
from models.ticket import TicketModel, TicketTypeModel, TicketOrderModel

from services.mongodb import MongodbService


class DashboardHandler(JsonHandler):
    @admin_auth_async
    async def get(self, *args, **kwargs):
        total_company_count = await CompanyModel.count({'enabled': True})
        total_user_count = await UserModel.count({'enabled': True})
        total_content_count = await ContentModel.count({'enabled': True})
        total_ticket_count = await TicketModel.count({'enabled': True})
        self.response['data'] = {
            'total_company_count': total_company_count,
            'total_user_count': total_user_count,
            'total_content_count': total_content_count,
            'total_ticket_count': total_ticket_count,
            'ticket_count': {
                'pend': 0,
                'send': 0,
                'register': 0,
                'pay': 0,
                'use': 0,
                'cancel': 0
            },
            'gender_count': {
                'male': 0,
                'female': 0
            }
        }
        # aggregate tickets
        pipeline = [
            {
                '$group': {
                    '_id': '$status',
                    'cnt': {
                        '$sum': 1
                    }
                }
            }
        ]
        res = await TicketModel.aggregate(pipeline, 10)
        for r in res:
            self.response['data']['ticket_count'][r['_id']] = r['cnt']

        # aggregate top contents
        pipeline = [
            {
                '$group': {
                    '_id': '$content_oid',
                    'ticket_cnt': {
                        '$sum': 1
                    }
                }
            },
            {
                '$sort': {
                    "ticket_cnt": -1
                }
            },
            {
                '$limit': 5
            }
        ]
        top_contents = await TicketModel.aggregate(pipeline, 5)
        for rc in top_contents:
            rc['content'] = await ContentModel.get_id(rc['_id'], fields=[('name')])
        self.response['data']['top_contents'] = top_contents

        # aggregate genders
        pipeline = [
            {
                '$group': {
                    '_id': '$gender',
                    'count': {
                        '$sum': 1
                    }
                }
            }
        ]
        res = await UserModel.aggregate(pipeline, 10)
        for r in res:
            self.response['data']['gender_count'][r['_id']] = r['count']
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class DashboardContentHandler(JsonHandler):
    @admin_auth_async
    async def get(self, *args, **kwargs):
        content_oid = kwargs.get('_id', None)
        if not content_oid or len(content_oid) != 24:
            raise HTTPError(400, 'invalid content_oid')
        self.response['data'] = {
            'ticket_count': {
                'pend': 0,
                'send': 0,
                'register': 0,
                'pay': 0,
                'use': 0,
                'cancel': 0
            },
            'avg_age': {
                'male': 0,
                'female': 0
            },
            'gender_count': {
                'register': {
                    'male': 0,
                    'female': 0
                },
                'use': {
                    'male': 0,
                    'female': 0
                }
            },
            'revenue': {
                'cash': 0,
                'creditcard': 0
            },
            'pre_revenue': {
                'amount': 0,
                'count': 0
            },
            'top_ticket_types': [],
            'top_ticket_orders': []
        }
        query = {
            'content_oid': ObjectId(content_oid),
            'enabled': True
        }
        # use aggregate for ticket count
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
        res = await TicketModel.aggregate(pipeline, 10)
        for r in res:
            self.response['data']['ticket_count'][r['_id']] = r['cnt']

        # use aggregate for genders
        pipeline = [
            {
                '$match': {
                    'content_oid': ObjectId(content_oid),
                    'status': TicketModel.Status.use.name
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
                '$unwind': {
                    'path': '$receive_user'
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
        res = await TicketModel.aggregate(pipeline, 5)
        for r in res:
            self.response['data']['gender_count']['use'][r['_id']] = r['count']

        # register aggregate for genders
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
                '$unwind': {
                    'path': '$receive_user'
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
        res = await TicketModel.aggregate(pipeline, 5)
        for r in res:
            self.response['data']['gender_count']['register'][r['_id']] = r['count']

        # use aggregate for top ticket type
        pipeline = [
            {
                '$match': {'content_oid': ObjectId(content_oid)}
            },
            {
                '$group': {
                    '_id': '$ticket_type_oid',
                    'ticket_cnt': {
                        '$sum': 1
                    }
                }
            },
            {
                '$sort': {
                    "ticket_cnt": -1
                }
            },
            {
                '$limit': 20
            }
        ]
        top_ticket_types = await TicketModel.aggregate(pipeline, 20)
        for ttt in top_ticket_types:
            ttt['ticket_type'] = await TicketTypeModel.get_id(ttt['_id'], fields=[('name'), ('desc')])
            ttt['ticket_register_cnt'] = await TicketModel.count({'ticket_type_oid': ttt['_id'], 'status': TicketModel.Status.register.name})
            ttt['ticket_pay_cnt'] = await TicketModel.count({'ticket_type_oid': ttt['_id'], 'status': TicketModel.Status.pay.name})
            ttt['ticket_use_cnt'] = await TicketModel.count({'ticket_type_oid': ttt['_id'], 'status': TicketModel.Status.use.name})
        self.response['data']['top_ticket_types'] = top_ticket_types

        # use aggregate for top ticket order
        pipeline = [
            {
                '$match': {'content_oid': ObjectId(content_oid)}
            },
            {
                '$group': {
                    '_id': '$ticket_order_oid',
                    'ticket_cnt': {
                        '$sum': 1
                    }
                }
            },
            {
                '$sort': {
                    "ticket_cnt": -1
                }
            },
            {
                '$limit': 50
            }
        ]
        top_ticket_orders = await TicketModel.aggregate(pipeline, 50)
        ttos = list()
        for tto in top_ticket_orders:
            if tto['_id']:
                tto['ticket_order'] = await TicketOrderModel.get_id(tto['_id'])
                tto['ticket_type'] = await TicketTypeModel.get_id(tto['ticket_order']['ticket_type_oid'])
                tto['ticket_register_cnt'] = await TicketModel.count({'ticket_order_oid': tto['_id'], 'status': TicketModel.Status.register.name})
                tto['ticket_pay_cnt'] = await TicketModel.count({'ticket_order_oid': tto['_id'], 'status': TicketModel.Status.pay.name})
                tto['ticket_use_cnt'] = await TicketModel.count({'ticket_order_oid': tto['_id'], 'status': TicketModel.Status.use.name})
                tto['ticket_cancel_cnt'] = await TicketModel.count({'ticket_order_oid': tto['_id'], 'status': TicketModel.Status.cancel.name})
                ttos.append(tto)
        self.response['data']['top_ticket_orders'] = ttos

        #user aggregate for revenue
        pipeline = [
            {
                '$match': {
                    'content_oid': ObjectId(content_oid),
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

        # count pre_revenue
        pipeline = [
            {
                '$match': {
                    'content_oid': ObjectId(content_oid),
                    'status': TicketModel.Status.pay.name
                }
            },
            {
                '$unwind': {'path': '$days'}
            },
            {
                '$group': {
                    '_id': '$status',
                    'pre_revenue': {
                        '$sum': '$days.fee.price'
                    },
                    'count': {
                        '$sum': 1
                    }
                }
            }
        ]
        aggs = await TicketModel.aggregate(pipeline, 5)
        if aggs:
            self.response['data']['pre_revenue'] = {
                'amount': aggs[0]['pre_revenue'],
                'count': aggs[0]['count']
            }
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()
