# -*- coding: utf-8 -*-

from tornado.web import HTTPError

from common.decorators import admin_auth_async

from handlers.base import JsonHandler
from models.invitation import InvitationModel


class DashboardHandler(JsonHandler):
    # @admin_auth_async
    async def get(self, *args, **kwargs):
        total_users_count = await InvitationModel.count({'enabled': True})
        total_visitors_count = await InvitationModel.count({'enabled': True, 'entered': True})
        total_visitors_fee_count = await InvitationModel.count({'enabled': True, 'entered': True, 'fee.enabled': True})
        self.response['data'] = {
            'total_users_count': total_users_count,
            'total_visitors_count': total_visitors_count,
            'total_visitors_fee_count': total_visitors_fee_count
        }
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()
