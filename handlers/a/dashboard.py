# -*- coding: utf-8 -*-

from tornado.web import HTTPError

from common.decorators import admin_auth_async

from handlers.base import JsonHandler
from models.company import CompanyModel
from models.user import UserModel
from models.content import ContentModel
from models.ticket import TicketModel


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
