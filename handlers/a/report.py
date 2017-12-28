# -*- coding: utf-8 -*-

from bson import ObjectId

from tornado.web import HTTPError

from common.decorators import admin_auth_async

from handlers.base import JsonHandler
from models.ticket import TicketModel, TicketLogModel

from services.mongodb import MongodbService


class ReportContentHandler(JsonHandler):
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
