# -*- coding: utf-8 -*-

from tornado.web import HTTPError

from common.decorators import admin_auth_async, parse_argument

from handlers.base import JsonHandler
from models.notification import NotificationModel


class NotificationListHandler(JsonHandler):
    # @admin_auth_async
    @parse_argument([('start', int, 0), ('size', int, 10), ])
    async def get(self, *args, **kwargs):
        parsed_args = kwargs.get('parsed_args')
        result = await NotificationModel.find(skip=parsed_args['start'], limit=parsed_args['size'])
        self.response['data'] = result 
        self.write_json()
