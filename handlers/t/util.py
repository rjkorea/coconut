# -*- coding: utf-8 -*-

from bson import ObjectId
from common.decorators import app_auth_async, tablet_auth_async, parse_argument
from tornado.web import HTTPError

from handlers.base import JsonHandler
from models.country import CountryModel


class CountryListHandler(JsonHandler):
    @app_auth_async
    @tablet_auth_async
    @parse_argument([('start', int, 0), ('size', int, 10), ('q', str, None)])
    async def get(self, *args, **kwargs):
        parsed_args = kwargs.get('parsed_args')
        if parsed_args['q']:
            q = {
                '$or': [
                    {'name': {'$regex': parsed_args['q']}},
                    {'code': {'$regex': parsed_args['q']}}
                ]
            }
        else:
            q = {}
        count = await CountryModel.count(query=q)
        result = await CountryModel.find(query=q, skip=parsed_args['start'], limit=parsed_args['size'], sort=[('name', 1)])
        self.response['data'] = result
        self.response['count'] = count
        self.write_json()
