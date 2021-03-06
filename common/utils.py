# -*- coding: utf-8 -*-


from bson import ObjectId
from json import JSONEncoder
from datetime import datetime


class ApiJSONEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        elif isinstance(o, datetime):
            return int(datetime.timestamp(o))
        else:
            return super(ApiJSONEncoder, self).default(o)


class Singleton(object):
    _instance = {}

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(cls, *args)
        return cls._instance
