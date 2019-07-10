# -*- coding: utf-8 -*-

from bson import ObjectId
from datetime import datetime

from tornado.web import HTTPError

from handlers.base import JsonHandler
from models.content import ContentModel
from models.ticket import TicketModel

from common import hashers
from common.decorators import parse_argument

from common.decorators import user_auth_async


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
        q = {
            'enabled': True,
            'is_private': False,
            'when.end': {
                '$gte': datetime.utcnow()
            }
        }
        count = await ContentModel.count(query=q)
        result = await ContentModel.find(query=q, fields=[('name'), ('when'), ('place'), ('images')], skip=parsed_args['start'], limit=parsed_args['size'])
        self.response['data'] = result
        self.response['count'] = count
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class ContentListMeHandler(JsonHandler):
    @user_auth_async
    async def get(self, *args, **kwargs):
        pipeline = [
            {
                '$match': {
                    'receive_user_oid': self.current_user['_id']
                }
            },
            {
                '$lookup': {
                    "from" : "content",
                    "localField" : "content_oid",
                    "foreignField" : "_id",
                    "as" : "content"
                }
            },
            {
                '$group': {
                    '_id': {
                        'content_oid': '$content_oid',
                        'content_name': '$content.name',
                        'content_when': '$content.when',
                        'ticket_count': {
                            '$sum': 1
                        }
                    }
                }
            }
        ]
        aggs = await TicketModel.aggregate(pipeline, 100)
        contents = list()
        for a in aggs:
            if a['_id']['content_when'][0]['end'] > datetime.utcnow():
                c = dict(
                    _id=a['_id']['content_oid'],
                    name=a['_id']['content_name'][0],
                    ticket_count=a['_id']['ticket_count'],
                    when_end=a['_id']['content_when'][0]['end']
                )
                contents.append(c)
        self.response['data'] = contents
        self.response['count'] = len(contents)
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()