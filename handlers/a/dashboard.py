# -*- coding: utf-8 -*-

from bson import ObjectId

from tornado.web import HTTPError

from common.decorators import admin_auth_async

from handlers.base import JsonHandler
from models.company import CompanyModel
from models.user import UserModel
from models.content import ContentModel
from models.ticket import TicketModel, TicketTypeModel, TicketOrderModel, TicketLogModel
from models.group import GroupTicketModel

from services.mongodb import MongodbService


class DashboardHandler(JsonHandler):
    @admin_auth_async
    async def get(self, *args, **kwargs):
        total_company_count = await CompanyModel.count({'enabled': True})
        total_user_count = await UserModel.count({})
        total_content_count = await ContentModel.count({'enabled': True})
        total_ticket_count = await TicketModel.count({'enabled': True})
        self.response['data'] = {
            'total_company_count': total_company_count,
            'total_user_count': total_user_count,
            'total_content_count': total_content_count,
            'total_ticket_count': total_ticket_count,
            'gender_count': {
                'male': 0,
                'female': 0
            },
            'monthly_new_users': [],
            'monthly_ticket_viral': [],
            'monthly_active_users': [],
            'last_7days_new_users': []
        }
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

        # aggregate monthly new users
        pipeline = [
            {
                '$group': {
                    '_id': {
                        '$dateToString': {
                            'format': '%Y-%m',
                            'date': '$created_at'
                        }
                    },
                    'count': {
                        '$sum': 1
                    }
                }
            },
            {
                '$sort': {
                    '_id': -1
                }
            }
        ]
        res = await UserModel.aggregate(pipeline, 12)
        for m in res:
            self.response['data']['monthly_new_users'].insert(0, m)

        # aggregate last 7days new users
        pipeline = [
            {
                '$group': {
                    '_id': {
                        '$dateToString': {
                            'format': '%Y-%m-%d',
                            'date': '$created_at'
                        }
                    },
                    'count': {
                        '$sum': 1
                    }
                }
            },
            {
                '$sort': {
                    '_id': -1
                }
            }
        ]
        res = await UserModel.aggregate(pipeline, 7)
        for m in res:
            self.response['data']['last_7days_new_users'].insert(0, m)

        # aggregate monthly ticket viral
        pipeline = [
            {
                '$group': {
                    '_id': {
                        '$dateToString': {
                            'format': '%Y-%m',
                            'date': '$created_at'
                        }
                    },
                    'count': {
                        '$sum': 1
                    }
                }
            },
            {
                '$sort': {
                    '_id': -1
                }
            }
        ]
        res = await TicketLogModel.aggregate(pipeline, 12)
        for m in res:
            self.response['data']['monthly_ticket_viral'].insert(0, m)

        # aggregate monthly active users
        pipeline = [
            {
                '$match': {
                    '$or': [
                        {'status': 'register'},
                        {'status': 'pay'},
                        {'status': 'use'},
                        {'status': 'cancel'}
                    ]
                },
            },
            {
                '$group': {
                    '_id': {
                        '$dateToString': {
                            'format': '%Y-%m',
                            'date': '$updated_at'
                        }
                    },
                    'count': {
                        '$sum': 1
                    }
                }
            },
            {
                '$sort': {
                    '_id': -1
                }
            }
        ]
        res = await TicketModel.aggregate(pipeline, 12)
        for m in res:
            self.response['data']['monthly_active_users'].insert(0, m)

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
            'revenue': {
                'amount': 0,
                'count': 0
            }
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

        # count revenue
        pipeline = [
            {
                '$match': {
                    '$and': [
                        {'content_oid': ObjectId(content_oid)},
                        {
                            '$or': [
                                {'status': TicketModel.Status.use.name},
                                {'status': TicketModel.Status.pay.name}
                            ]
                        }
                    ]
                }
            },
            {
                '$group': {
                    '_id': '$content_oid',
                    'revenue': {
                        '$sum': '$price'
                    },
                    'count': {
                        '$sum': 1
                    }
                }
            }
        ]
        aggs = await TicketModel.aggregate(pipeline, 5)
        if aggs:
            self.response['data']['revenue'] = {
                'amount': aggs[0]['revenue'],
                'count': aggs[0]['count']
            }
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()
