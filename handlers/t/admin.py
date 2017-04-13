# -*- coding: utf-8 -*-

from common.decorators import app_auth_async, tablet_auth_async
from tornado.web import HTTPError

from handlers.base import JsonHandler
from models.admin import AdminModel


class AdminHandler(JsonHandler):
    @app_auth_async
    @tablet_auth_async
    async def get(self, *args, **kwargs):
        self.response['data'] = self.current_user
        self.write_json()
