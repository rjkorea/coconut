# -*- coding: utf-8 -*-

from bson import ObjectId
from common.decorators import app_auth_async, tablet_auth_async, parse_argument
from tornado.web import HTTPError

from handlers.base import JsonHandler
from models.content import ContentModel


class DashboardHandler(JsonHandler):
    @app_auth_async
    @tablet_auth_async
    async def get(self, *args, **kwargs):
        _id = kwargs.get('_id', None)
        if not _id or len(_id) != 24:
            raise HTTPError(400, 'invalid _id')
        # content = await ContentModel.find_one({'_id': ObjectId(_id), 'user_oid': self.current_user['_id']})
        # if not content:
        #     raise HTTPError(400, 'not exist content')
        dashboard = dict(
            use=787,
            total=1242
        )
        self.response['data'] = dashboard
        self.write_json()
