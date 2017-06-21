# -*- coding: utf-8 -*-

from bson import ObjectId
from datetime import datetime

from tornado.web import HTTPError

from handlers.base import JsonHandler
from models.qna import QnaModel

from common.decorators import admin_auth_async, parse_argument


class QnaListHandler(JsonHandler):
    @admin_auth_async
    @parse_argument([('start', int, 0), ('size', int, 10), ('content_oid', str, None)])
    async def get(self, *args, **kwargs):
        parsed_args = kwargs.get('parsed_args')
        if 'content_oid' in parsed_args and parsed_args['content_oid']:
            q = {
                'content_oid': ObjectId(parsed_args['content_oid'])
            }
        else:
            q = {}
        count = await QnaModel.count(query=q)
        result = await QnaModel.find(query=q, skip=parsed_args['start'], limit=parsed_args['size'])
        self.response['data'] = result
        self.response['count'] = count
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class QnaHandler(JsonHandler):
    @admin_auth_async
    async def post(self, *args, **kwargs):
        # basic field
        admin_oid = self.current_user['_id']
        content_oid = self.json_decoded_body.get('content_oid', None)
        if not content_oid or len(content_oid) != 24:
            raise HTTPError(400, 'invalid content_oid')
        question = self.json_decoded_body.get('question', None)
        if not question or len(question) == 0:
            raise HTTPError(400, 'invalid question')
        answer = self.json_decoded_body.get('answer', None)
        if not answer or len(answer) == 0:
            raise HTTPError(400, 'invalid answer')
        qna = QnaModel(raw_data=dict(
            admin_oid=admin_oid,
            content_oid=ObjectId(content_oid),
            question=question,
            answer=answer
        ))
        await qna.insert()
        self.response['data'] = qna.data
        self.write_json()

    @admin_auth_async
    async def put(self, *args, **kwargs):
        _id = kwargs.get('_id', None)
        if not _id or len(_id) != 24:
            raise HTTPError(400, 'invalid _id')
        qna = await QnaModel.find_one({'_id': ObjectId(_id)})
        if not qna:
            raise HTTPError(400, 'not exist qna')
        query = {
            '_id': ObjectId(_id)
        }
        self.json_decoded_body['updated_at'] = datetime.utcnow()
        document = {
            '$set': self.json_decoded_body
        }
        self.response['data'] = await QnaModel.update(query, document)
        self.write_json()

    @admin_auth_async
    async def get(self, *args, **kwargs):
        _id = kwargs.get('_id', None)
        if not _id or len(_id) != 24:
            raise HTTPError(400, 'invalid _id')
        qna = await QnaModel.find_one({'_id': ObjectId(_id)})
        if not qna:
            raise HTTPError(400, 'not exist qna')
        self.response['data'] = qna
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()
