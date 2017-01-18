# -*- coding: utf-8 -*-

from bson import ObjectId
from datetime import datetime

from tornado.web import HTTPError

from common.decorators import admin_auth_async, parse_argument

from handlers.base import JsonHandler
from models.notification import NotificationModel


class NotificationHandler(JsonHandler):
    @admin_auth_async
    async def put(self, *args, **kwargs):
        _id = kwargs.get('_id', None)
        if not _id or len(_id) != 24:
            raise HTTPError(400, 'invalid _id')
        notification = await NotificationModel.find_one({'_id': ObjectId(_id)})
        if not notification:
            raise HTTPError(400, 'not exist _id')
        query = {
            '_id': ObjectId(_id)
        }
        self.json_decoded_body['updated_at'] = datetime.utcnow()
        document = {
            '$set': self.json_decoded_body
        }
        self.response['data'] = await NotificationModel.update(query, document)
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class NotificationListHandler(JsonHandler):
    @admin_auth_async
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

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()
