# -*- coding: utf-8 -*-

from bson import ObjectId
from common.decorators import app_auth_async, tablet_auth_async, parse_argument
from tornado.web import HTTPError

from handlers.base import JsonHandler
from models.content import ContentModel


class ContentListHandler(JsonHandler):
    @app_auth_async
    @tablet_auth_async
    @parse_argument([('start', int, 0), ('size', int, 10)])
    async def get(self, *args, **kwargs):
        parsed_args = kwargs.get('parsed_args')
        q = {
            'user_oid': self.current_user['_id']
        }
        count = await ContentModel.count(query=q)
        result = await ContentModel.find(query=q, skip=parsed_args['start'], limit=parsed_args['size'])
        self.response['data'] = result
        self.response['count'] = count
        self.write_json()


class ContentHandler(JsonHandler):
    @app_auth_async
    @tablet_auth_async
    async def get(self, *args, **kwargs):
        _id = kwargs.get('_id', None)
        if not _id or len(_id) != 24:
            raise HTTPError(400, 'invalid _id')
        content = await ContentModel.find_one({'_id': ObjectId(_id), 'user_oid': self.current_user['_id']})
        if not content:
            raise HTTPError(400, 'not exist content')
        self.response['data'] = content
        self.write_json()
