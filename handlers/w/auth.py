# -*- coding: utf-8 -*-

from datetime import datetime
from bson import ObjectId

from tornado.web import HTTPError

from handlers.base import JsonHandler
from models.user import UserModel

from common.decorators import parse_argument


class DuplicatedHandler(JsonHandler):
    @parse_argument([('email', str, None), ('mobile_number', str, None)])
    async def get(self, *args, **kwargs):
        parsed_args = kwargs.get('parsed_args')
        if not parsed_args['email'] and not parsed_args['mobile_number']:
            raise HTTPError(400, 'no params (email or mobile_number)')
        if parsed_args['email']:
            user = await UserModel.find_one({'email': parsed_args['email'], 'enabled': True})
            if user:
                self.response['data'] = 'OK'
            else:
                raise HTTPError(400, 'no exist email')
        elif parsed_args['mobile_number']:
            user = await UserModel.find_one({'mobile_number': parsed_args['mobile_number'], 'enabled': True})
            if user:
                self.response['data'] = 'OK'
            else:
                raise HTTPError(400, 'no exist mobile number')
        else:
            self.response['data'] = None
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()
