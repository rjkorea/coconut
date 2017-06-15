# -*- coding: utf-8 -*-

from bson import ObjectId

from tornado.web import HTTPError

from handlers.base import JsonHandler
from models.qna import QnaModel

from common.decorators import user_auth_async, parse_argument


class QnaListHandler(JsonHandler):
    @user_auth_async
    @parse_argument([('start', int, 0), ('size', int, 10), ('content_oid', str, None)])
    async def get(self, *args, **kwargs):
        parsed_args = kwargs.get('parsed_args')
        q = {
            'content_oid': ObjectId(parsed_args['content_oid'])
        }
        count = await QnaModel.count(query=q)
        result = await QnaModel.find(query=q, skip=parsed_args['start'], limit=parsed_args['size'])
        self.response['data'] = result
        self.response['count'] = count
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()
