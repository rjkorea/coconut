# -*- coding: utf-8 -*-

from datetime import datetime
from bson import ObjectId

from tornado.web import HTTPError

from common.decorators import admin_auth_async, parse_argument

from handlers.base import JsonHandler
from models.place import PlaceModel
from models.admin import AdminModel


class PlaceListHandler(JsonHandler):
    @admin_auth_async
    @parse_argument([('start', int, 0), ('size', int, 10), ('q', str, None)])
    async def get(self, *args, **kwargs):
        parsed_args = kwargs.get('parsed_args')
        q = dict()
        if 'q' in parsed_args and parsed_args['q']:
            q['$or'] = [
                {'name': {'$regex': parsed_args['q']}},
                {'mobile_number': {'$regex': parsed_args['q']}},
                {'area': {'$regex': parsed_args['q']}},
                {'number': {'$regex': parsed_args['q']}}
            ]
        count = await PlaceModel.count(query=q)
        result = await PlaceModel.find(query=q, skip=parsed_args['start'], limit=parsed_args['size'])
        self.response['data'] = result
        self.response['count'] = count
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class PlaceHandler(JsonHandler):
    @admin_auth_async
    async def post(self, *args, **kwargs):
        # basic field
        admin_oid = self.current_user['_id']
        name = self.json_decoded_body.get('name', None)
        if not name or len(name) == 0:
            raise HTTPError(400, 'invalid name')
        mobile_number = self.json_decoded_body.get('mobile_number', None)
        if not mobile_number or len(mobile_number) == 0:
            raise HTTPError(400, 'invalid mobile_number')
        area = self.json_decoded_body.get('area', None)
        if not area or len(area) == 0:
            raise HTTPError(400, 'invalid area')
        number = self.json_decoded_body.get('number', None)
        if not number or len(number) == 0:
            raise HTTPError(400, 'invalid number')
        query = {
            'area': area,
            'number': number
        }
        duplicated_place = await PlaceModel.find_one(query)
        if duplicated_place:
            raise HTTPError(400, 'duplicated_place')

        place = PlaceModel(raw_data=dict(
            admin_oid=admin_oid,
            name=name,
            mobile_number=mobile_number,
            area=area,
            number=number
        ))
        await place.insert()
        self.response['data'] = place.data
        self.write_json()

    @admin_auth_async
    async def put(self, *args, **kwargs):
        _id = kwargs.get('_id', None)
        if not _id or len(_id) != 24:
            raise HTTPError(400, 'invalid _id')
        place = await PlaceModel.find_one({'_id': ObjectId(_id)})
        if not place:
            raise HTTPError(400, 'not exist _id')
        query = {
            'area': self.json_decoded_body['area'],
            'number': self.json_decoded_body['number'],
            '_id': {'$ne': ObjectId(_id)}
        }
        duplicated_place = await PlaceModel.find_one(query)
        if duplicated_place:
            raise HTTPError(400, 'duplicated place')
        query = {
            '_id': ObjectId(_id),
        }
        self.json_decoded_body['updated_at'] = datetime.utcnow()
        document = {
            '$set': self.json_decoded_body
        }
        self.response['data'] = await PlaceModel.update(query, document)
        self.write_json()

    @admin_auth_async
    async def get(self, *args, **kwargs):
        _id = kwargs.get('_id', None)
        if not _id or len(_id) != 24:
            raise HTTPError(400, 'invalid _id')
        place = await PlaceModel.find_one({'_id': ObjectId(_id)})
        if not place:
            raise HTTPError(400, 'not exist place')
        self.response['data'] = place
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()
