# -*- coding: utf-8 -*-

from bson import ObjectId

from tornado.web import HTTPError

from common.decorators import admin_auth_async

from handlers.base import JsonHandler
from models.company import CompanyModel
from models.user import UserModel
from models.content import ContentModel
from models.ticket import TicketModel, TicketTypeModel

from services.mongodb import MongodbService


class DashboardHandler(JsonHandler):
    @admin_auth_async
    async def get(self, *args, **kwargs):
        total_company_count = await CompanyModel.count({'enabled': True})
        total_user_count = await UserModel.count({'enabled': True})
        total_content_count = await ContentModel.count({'enabled': True})
        self.response['data'] = {
            'total_company_count': total_company_count,
            'total_user_count': total_user_count,
            'total_content_count': total_content_count,
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
        ticket = dict()
        for r in res:
            ticket[r['_id']] = r['cnt']
        self.response['data']['ticket_count'] = ticket

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
        genders = dict()
        for r in res:
            genders[r['_id']] = r['count']
        self.response['data']['gender_count'] = genders
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
                'use': 0,
                'total': 0
            },
            'avg_age': {
                'male': 0,
                'female': 0
            },
            'revenue': {
                'cash': 0,
                'creditcard': 0
            },
            'top_ticket_types': []
        }
        query = {
            'content_oid': ObjectId(content_oid),
            'enabled': True
        }
        self.response['data']['ticket_count']['total'] = await TicketModel.count(
            {
                'content_oid': ObjectId(content_oid),
                'enabled': True
            }
        )
        self.response['data']['ticket_count']['use'] = await TicketModel.count(
            {
                'content_oid': ObjectId(content_oid),
                'enabled': True,
                'status': 'use'
            }
        )

        # use aggregate
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
                '$limit': 5
            }
        ]
        top_ticket_types = await TicketModel.aggregate(pipeline, 5)
        for ttt in top_ticket_types:
            ttt['ticket_type'] = await TicketTypeModel.get_id(ttt['_id'], fields=[('name')])
        self.response['data']['top_ticket_types'] = top_ticket_types
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()
