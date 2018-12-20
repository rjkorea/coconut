# -*- coding: utf-8 -*-

from bson import ObjectId
from datetime import datetime

from tornado.web import HTTPError

from common.decorators import user_auth_async

from handlers.base import JsonHandler
from models.user import UserModel


class UserHandler(JsonHandler):
    async def delete(self, *args, **kwargs):
        _id = kwargs.get('_id', None)
        if not _id or len(_id) != 24:
            raise HTTPError(400, 'invalid _id')
        user = await UserModel.find_one({'_id': ObjectId(_id), 'enabled': True})
        if not user:
            raise HTTPError(400, 'no exist user')
        res = await UserModel.update(
            {'_id': user['_id'], 'enabled': True},
            {
                '$set':{
                    'enabled': False, 
                    'updated_at': datetime.utcnow()
                }
            },
            False, False)
        self.response['data'] = res
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()

