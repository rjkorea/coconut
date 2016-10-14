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
