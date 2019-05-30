# -*- coding: utf-8 -*-

from bson import ObjectId
import requests
from common.decorators import app_auth_async, tablet_auth_async, parse_argument
from tornado.web import HTTPError

from handlers.base import JsonHandler
from models.country import CountryModel


class CountryListHandler(JsonHandler):
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


class ExchangeRateHandler(JsonHandler):
    async def get(self, *args, **kwargs):
        url = 'https://quotation-api-cdn.dunamu.com/v1/forex/recent?codes=FRX.KRWUSD'
        res = requests.get(url)
        krwusd = res.json()[0]
        self.response['data'] = {
            'updated_at': krwusd['modifiedAt'],
            'currency': {
                'name': krwusd['currencyName'],
                'code': krwusd['currencyCode']
            },
            'provider': krwusd['provider'],
            'base_price': krwusd['basePrice'],
            'name': krwusd['name'],
            'change_rate': krwusd['changeRate']
        }
        self.write_json()
