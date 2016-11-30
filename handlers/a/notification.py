# -*- coding: utf-8 -*-

from bson import ObjectId
from tornado.web import HTTPError

from common.decorators import admin_auth_async, parse_argument

from handlers.base import JsonHandler
from models.notification import NotificationModel


class NotificationListHandler(JsonHandler):
    # @admin_auth_async
    @parse_argument([('start', int, 0), ('size', int, 10), ('_id', str, None)])
    async def get(self, *args, **kwargs):
        parsed_args = kwargs.get('parsed_args')
        if not parsed_args['_id']:
            raise HTTPError(400, 'invalid _id')
        query = {
            'admin_oid': ObjectId(parsed_args['_id']),
            'enabled': True
        }
        result = await NotificationModel.find(query=query, skip=parsed_args['start'], limit=parsed_args['size'])
        self.response['data'] = result 
        count = await NotificationModel.count(query)
        self.response['count'] = count
        query['read'] = False
        unread_count = await NotificationModel.count(query)
        self.response['unread_count'] = unread_count
        self.write_json()
