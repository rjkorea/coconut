# -*- coding: utf-8 -*-

from bson import ObjectId

from common import hashers

from models.base import BaseModel


class CountryModel(BaseModel):
    MONGO_COLLECTION = 'country'

    def __init__(self, *args, **kwargs):
        super(CountryModel, self).__init__(*args, **kwargs)

    @property
    def specification(self):
        specification = super(CountryModel, self).specification
        specification.extend([
            {
                'key': 'seq',
                'type': int,
                'default': None
            },
            {
                'key': 'name',
                'type': str,
                'default': None
            },
            {
                'key': 'code',
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
