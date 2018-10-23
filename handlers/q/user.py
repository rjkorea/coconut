# -*- coding: utf-8 -*-

from datetime import datetime
from bson import ObjectId

from tornado.web import HTTPError

from common.decorators import admin_auth_async

from handlers.base import JsonHandler
from models.user import UserModel


class UserHandler(JsonHandler):
    @admin_auth_async
    async def get(self, *args, **kwargs):
        _id = kwargs.get('_id', None)
        if not _id or len(_id) != 24:
            raise HTTPError(400, 'invalid _id')
        user = await UserModel.find_one({'_id': ObjectId(_id)}, fields=[('name'), ('mobile_number')])
        if not user:
            raise HTTPError(400, 'not exist _id')
        self.response['data'] = user
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()

