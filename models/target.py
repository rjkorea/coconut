# -*- coding: utf-8 -*-

from bson import ObjectId

from common import hashers

from models.base import BaseModel


class TargetModel(BaseModel):
    MONGO_COLLECTION = 'target'
    TYPE = ('lms', 'kakaotalk')

    def __init__(self, *args, **kwargs):
        super(TargetModel, self).__init__(*args, **kwargs)

    @property
    def specification(self):
        specification = super(TargetModel, self).specification
        specification.extend([
            {
                'key': 'type',
                'type': str,
                'default': None
            },
            {
                'key': 'admin_oid',
                'type': ObjectId,
                'default': None
            },
            {
                'key': 'content_oid',
                'type': ObjectId,
                'default': None
            },
            {
                'key': 'ticket_type_oids',
                'type': list,
                'default': None
            },
            {
                'key': 'status',
                'type': list,
                'default': None
            },
            {
                'key': 'enabled',
                'type': bool,
                'default': (lambda: True)
            },
            {
                'key': 'sms',
                'type': dict,
                'default': None
            },
            {
                'key': 'count',
                'type': int,
                'default': None
            },
            {
                'key': 'success_count',
                'type': int,
                'default': None
            },
        ])
        return specification
