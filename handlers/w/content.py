# -*- coding: utf-8 -*-

from bson import ObjectId

from tornado.web import HTTPError

from handlers.base import JsonHandler
from models.content import ContentModel

from common import hashers


class ContentHandler(JsonHandler):
    async def get(self, *args, **kwargs):
        _id = kwargs.get('_id', None)
        if not _id or len(_id) != 24:
            raise HTTPError(400, 'invalid _id')
        content = await ContentModel.find_one({'_id': ObjectId(_id)})
        if not content:
            raise HTTPError(400, 'not exist content')
        self.response['data'] = content
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()
