# -*- coding: utf-8 -*-

from bson import ObjectId

from tornado.web import HTTPError

from handlers.base import JsonHandler
from models.content import ContentModel

from common import hashers
from common.decorators import parse_argument


class ContentHandler(JsonHandler):
    async def get(self, *args, **kwargs):
        _id = kwargs.get('_id', None)
        if not _id or (len(_id) != 24 and len(_id) != 7):
            raise HTTPError(400, 'invalid _id (user _id or short_id field of content)')
        if len(_id) == 24:
            content = await ContentModel.find_one({'_id': ObjectId(_id)})
        elif len(_id) == 7:
            content = await ContentModel.find_one({'short_id': _id})
        if not content:
            raise HTTPError(400, 'not exist content')
        self.response['data'] = content
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class ContentListHandler(JsonHandler):
    @parse_argument([('start', int, 0), ('size', int, 10), ('q', str, None)])
    async def get(self, *args, **kwargs):
        parsed_args = kwargs.get('parsed_args')
        count = await ContentModel.count(query={})
        result = await ContentModel.find(query={}, fields=[('name'), ('when'), ('place'), ('image')], skip=parsed_args['start'], limit=parsed_args['size'])
        self.response['data'] = result
        self.response['count'] = count
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()