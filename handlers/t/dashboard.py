# -*- coding: utf-8 -*-

from bson import ObjectId
from common.decorators import app_auth_async, tablet_auth_async, parse_argument
from tornado.web import HTTPError

from handlers.base import JsonHandler
from models.ticket import TicketModel


class DashboardHandler(JsonHandler):
    @app_auth_async
    @tablet_auth_async
    async def get(self, *args, **kwargs):
        _id = kwargs.get('_id', None)
        if not _id or len(_id) != 24:
            raise HTTPError(400, 'invalid _id')
        total = await TicketModel.count({'content_oid': ObjectId(_id)})
        use = await TicketModel.count({'content_oid': ObjectId(_id), 'status': 'use'})
        pend = await TicketModel.count({'content_oid': ObjectId(_id), 'status': 'pend'})
        send = await TicketModel.count({'content_oid': ObjectId(_id), 'status': 'send'})
        register = await TicketModel.count({'content_oid': ObjectId(_id), 'status': 'register'})
        dashboard = dict(
            pend=pend,
            register=register,
            send=send,
            use=use,
            total=total
        )
        self.response['data'] = dashboard
        self.write_json()
