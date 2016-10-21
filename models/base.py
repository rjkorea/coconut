# -*- coding: utf-8 -*-

from bson.objectid import ObjectId
from datetime import datetime

from services.mongodb import MongodbService


class BaseModel(object):
    MONGO_COLLECTION = None

    def __init__(self, *args, **kwargs):
        raw_data = kwargs.pop('raw_data', dict())
        self.data = self.refine(raw_data)
    
    @property
    def specification(self):
        return [
            {
                'key': '_id',
                'type': ObjectId,
                'default': None
            },
            {
                'key': 'created_at',
                'type': datetime,
                'default':datetime.utcnow 
            },
            {
                'key': 'updated_at',
                'type': datetime,
                'default': datetime.utcnow
            }
        ]
    
    @classmethod
    async def find_one(cls, query={}, fields=None):
        result = await MongodbService().client[cls.MONGO_COLLECTION].find_one(query, fields)
        return result

    @classmethod
    async def find(cls, query={}, fields=None, sort=[('created_at', -1)], skip=0, limit=10):
        cursor = MongodbService().client[cls.MONGO_COLLECTION].find(query, fields).sort(sort).skip(skip).limit(limit)
        result = await cursor.to_list(length=limit if limit > 0 else None)
        return result

    @classmethod
    async def count(cls, query={}):
        result = await MongodbService().client[cls.MONGO_COLLECTION].find(query).count()
        return result

    @classmethod
    async def update(cls, query, document, upsert=False, multi=False):
        if query is None or not isinstance(query, dict):
            raise ValueError('Invalid query')
        if document is None or not isinstance(document, dict):
            raise ValueError('Invalid doocument')
        result = await MongodbService().client[cls.MONGO_COLLECTION].update(query, document, upsert=upsert, multi=multi)
        return result

    async def insert(self):
        if not hasattr(self, 'data'):
            raise ValueError('instance does not have atturibute "data"')
        if '_id' in self.data:
            del self.data._id
        result = await MongodbService().client[self.MONGO_COLLECTION].insert(self.data)
        if result:
            self._id = result
        return result

    def refine(self, raw_data):
        result = dict()
        for spec in self.specification:
            key = spec['key']
            if key in raw_data:
                result[key] = raw_data[key]
            else:
                default_generator = spec['default']
                if default_generator:
                    result[key] = default_generator()
        return result
