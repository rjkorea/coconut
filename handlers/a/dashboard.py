# -*- coding: utf-8 -*-

from bson import ObjectId

from tornado.web import HTTPError

from common.decorators import admin_auth_async

from handlers.base import JsonHandler
from models.company import CompanyModel
from models.user import UserModel
from models.content import ContentModel
from models.ticket import TicketModel, TicketTypeModel


class DashboardHandler(JsonHandler):
    @admin_auth_async
    async def get(self, *args, **kwargs):
        total_company_count = await CompanyModel.count({'enabled': True})
        total_user_count = await UserModel.count({'enabled': True})
        total_content_count = await ContentModel.count({'enabled': True})
        total_ticket_count = await TicketModel.count({'enabled': True})
        recent_contents = await ContentModel.find(query={'enabled': True}, fields=[('name')], limit=5)
        self.response['data'] = {
            'total_ticket_count': total_ticket_count,
            'total_company_count': total_company_count,
            'total_user_count': total_user_count,
            'total_content_count': total_content_count,
            'recent_contents': recent_contents
        }
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
            'recent_ticket_types': []
        }
        query = {
            'content_oid': ObjectId(content_oid),
            'enabled': True
        }
        self.response['data']['recent_ticket_types'] = await TicketTypeModel.find(
            query = {
                    'content_oid': ObjectId(content_oid),
                    'enabled': True
            },
            fields=[('name')], limit=5)
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
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()
