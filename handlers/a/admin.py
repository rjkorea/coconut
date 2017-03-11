# -*- coding: utf-8 -*-

from datetime import datetime
from bson import ObjectId

from common.decorators import admin_auth_async, parse_argument

from handlers.base import JsonHandler
from models.admin import AdminModel


class AdminListHandler(JsonHandler):
    @admin_auth_async
    @parse_argument([('start', int, 0), ('size', int, 10), ])
    async def get(self, *args, **kwargs):
        parsed_args = kwargs.get('parsed_args')
        result = await AdminModel.find(skip=parsed_args['start'], limit=parsed_args['size'])
        self.response['data'] = result
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()
