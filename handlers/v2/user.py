# -*- coding: utf-8 -*-

from bson import ObjectId
from datetime import datetime

from tornado.web import HTTPError

from common import hashers
from common.decorators import user_access_token_auth_async, parse_argument

from handlers.base import JsonHandler, MultipartFormdataHandler
from models.user import UserModel, UserAutologinModel
from models.session import UserSessionModel
from models import send_sms

from services.s3 import S3Service

import settings


class UserMeHandler(JsonHandler):
    @user_access_token_auth_async
    async def get(self, *args, **kwargs):
        user = await UserModel.find_one({'_id': self.current_user['_id']})
        if not user:
            raise HTTPError(400, 'not exist user')
        self.response['data'] = user
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()
