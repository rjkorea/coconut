# -*- coding: utf-8 -*-

from bson import ObjectId

from tornado.web import HTTPError

import requests

from handlers.base import JsonHandler
from models.content import ContentModel
from models.ticket import TicketOrderModel

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
        q = {
            'content_oid': ObjectId(_id),
            'type': 'general',
            'enabled': True
        }
        to_count = await TicketOrderModel.count(q)
        if to_count:
            content['ticket_open'] = True
        else:
            content['ticket_open'] = False
        self.response['data'] = content
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class ContentListHandler(JsonHandler):
    @parse_argument([('start', int, 0), ('size', int, 10), ('q', str, None)])
    async def get(self, *args, **kwargs):
        parsed_args = kwargs.get('parsed_args')
        count = await ContentModel.count(query={'enabled': True, 'company_oid': ObjectId('5922bc83c8bd9535771cf837')})
        result = await ContentModel.find(query={'enabled': True, 'company_oid': ObjectId('5922bc83c8bd9535771cf837')}, fields=[('name'), ('desc'), ('when'), ('place'), ('image')], skip=parsed_args['start'], limit=parsed_args['size'])
        self.response['data'] = result
        self.response['count'] = count
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class SnsContentListHandler(JsonHandler):
    async def get(self, *args, **kwargs):
        url = 'https://graph.facebook.com/v2.12/tkitme/feed'
        params = dict(
            access_token='EAAFG94tLB6MBAC325Jq3LtQOPuozbeHpFIUmeeEvujPlhBVWNbpW4lCD0ZCXRZBk60IZAD0xeZCJzAgp0ZCP8pabbO8tixU7KZCCbbMTqdPLrrRnLYDbfPZAHuBtDpyZCGutv9ET7o2FDgXW455ScteQgUOb9I4GUO1lQ2E5ZCz7dZBAZDZD',
            fields='type,message,name,link,created_time,picture,full_picture,description',
            limit=10
        )
        res = requests.get(url, params)
        self.response['data'] = res.json()['data']
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()
