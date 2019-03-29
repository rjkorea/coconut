# -*- coding: utf-8 -*-

from bson import ObjectId

from tornado.web import HTTPError

from handlers.base import JsonHandler
from models.content import ContentModel

from common import hashers
from common.decorators import admin_auth_async, parse_argument


class ContentListMeHandler(JsonHandler):
    @admin_auth_async
    @parse_argument([('start', int, 0), ('size', int, 20)])
    async def get(self, *args, **kwargs):
        parsed_args = kwargs.get('parsed_args')
        count = await ContentModel.count(query={'company_oid': self.current_user['company_oid'], 'enabled': True})
        result = await ContentModel.find(query={'company_oid': self.current_user['company_oid'], 'enabled': True}, fields=[('name'), ('when'), ('place'), ('images'), ('company_oid')], skip=parsed_args['start'], limit=parsed_args['size'])
        self.response['data'] = result
        self.response['count'] = count
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()