# -*- coding: utf-8 -*-

from bson import ObjectId

from models.base import BaseModel


class PlaceModel(BaseModel):
    MONGO_COLLECTION = 'place'

    def __init__(self, *args, **kwargs):
        super(PlaceModel, self).__init__(*args, **kwargs)

    @property
    def specification(self):
        specification = super(PlaceModel, self).specification
        specification.extend([
            {
                'key': 'name',
                'type': str,
                'default': None
            },
            {
                'key': 'mobile_number',
                'type': str,
                'default': None
            },
            {
                'key': 'admin_oid',
                'type': ObjectId,
                'default': None
            },
            {
                'key': 'area',
                'type': str,
                'default': None
            },
            {
                'key': 'number',
                'type': str,
                'default': None
            },
            {
                'key': 'enabled',
                'type': bool,
                'default': (lambda: True)
            },
        ])
        return specification
