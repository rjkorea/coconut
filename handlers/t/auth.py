# -*- coding: utf-8 -*-

from bson import ObjectId
from common.decorators import app_auth_async, tablet_auth_async
from tornado.web import HTTPError

from handlers.base import JsonHandler, WSHandler
from models.user import UserModel
from models.ticket import TicketModel
from models.content import ContentModel


class AuthHandler(JsonHandler):
    @app_auth_async
    @tablet_auth_async
    async def put(self, *args, **kwargs):
        content_oid = self.json_decoded_body.get('content_oid', None)
        if not content_oid or len(content_oid) != 24:
            raise HTTPError(400, 'invalid content_oid')
        content = await ContentModel.find_one({'_id': ObjectId(content_oid)})
        if not content:
            raise HTTPError(400, 'not exist content')
        mobile_number = self.json_decoded_body.get('mobile_number', None)
        if not mobile_number or len(mobile_number) == 0:
            raise HTTPError(400, 'invalid mobile_number')
        auth_user = await UserModel.find_one({'mobile_number': mobile_number})
        if not auth_user:
            raise HTTPError(400, 'not exist mobile number')
        ws_data = dict(
            tablet_code=self.current_user['tablet_code'],
            auth_user_oid=str(auth_user['_id']),
            content_oid=str(content['_id'])
        )
        WSHandler.write_to_clients(ws_data)
        self.response['data'] = auth_user
        self.write_json()
