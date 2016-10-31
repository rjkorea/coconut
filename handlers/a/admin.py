# -*- coding: utf-8 -*-

from datetime import datetime
from bson import ObjectId

from common.decorators import admin_auth_async

from tornado.web import HTTPError

from handlers.base import JsonHandler
from models.admin import AdminModel




class AdminListHandler(JsonHandler):
    @admin_auth_async
    async def get(self, *args, **kwargs):
        result = await AdminModel.find()
        self.response['data'] = result 
        self.write_json()
