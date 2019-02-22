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


class StatsContentHandler(JsonHandler):
    @admin_auth_async
    async def get(self, *args, **kwargs):
        content_oid = kwargs.get('_id', None)
        if not content_oid or len(content_oid) != 24:
            raise HTTPError(400, 'invalid content_oid')
        content = await ContentModel.get_id(ObjectId(content_oid), fields=[('name')])
        self.response['data'] = {
            'content': content['name'],
            'total_viral': 0,
            'revenue': {
                'amount': 0,
                'count': 0
            },
            'ticket_count': {
                'pend': 0,
                'send': 0,
                'register': 0,
                'pay': 0,
                'use': 0,
                'cancel': 0
            },
            'daily_ticket_viral': []
        }
        q = {
            'content_oid': ObjectId(content_oid),
            'action': TicketLogModel.Status.send.name
        }
        self.response['data']['total_viral'] = await TicketLogModel.count(query=q)
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
                '$unwind': {'path': '$days'}
            },
            {
                '$group': {
                    '_id': '$content_oid',
                    'revenue': {
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
            self.response['data']['revenue'] = {
                'amount': aggs[0]['revenue'],
                'count': aggs[0]['count']
            }
        # aggregate tickets
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
        # aggregate monthly ticket viral
        pipeline = [
            {
                '$match': {
                    'content_oid': ObjectId(content_oid)
                }
            },
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
        res = await TicketLogModel.aggregate(pipeline, 14)
        for m in res:
            self.response['data']['daily_ticket_viral'].insert(0, m)
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()
