# -*- coding: utf-8 -*-

from bson import ObjectId

from common import hashers

from models.base import BaseModel


class ContentModel(BaseModel):
    MONGO_COLLECTION = 'content'

    def __init__(self, *args, **kwargs):
        super(ContentModel, self).__init__(*args, **kwargs)

    @property
    def specification(self):
        specification = super(ContentModel, self).specification
        specification.extend([
            {
                'key': 'user_oid',
                'type': ObjectId,
                'default': None
            },
            {
                'key': 'name',
                'type': str,
                'default': None
            },
            {
                'key': 'desc',
                'type': str,
                'default': None
            },
            {
                'key': 'image',
                'type': dict,
                'default': None
            },
            {
                'key': 'place',
                'type': str,
                'default': None
            },
            {
                'key': 'genre',
                'type': list,
                'default': None
            },
            {
                'key': 'lineup',
                'type': list,
                'default': None
            },
            {
                'key': 'when',
                'type': dict,
                'default': None
            },
            {
                'key': 'enabled',
                'type': bool,
                'default': (lambda: True)
            },
        ])
        return specification
