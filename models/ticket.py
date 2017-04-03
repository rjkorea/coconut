# -*- coding: utf-8 -*-

from bson import ObjectId

from common import hashers

from models.base import BaseModel


class TicketTypeModel(BaseModel):
    MONGO_COLLECTION = 'ticket_type'

    def __init__(self, *args, **kwargs):
        super(TicketTypeModel, self).__init__(*args, **kwargs)

    @property
    def specification(self):
        specification = super(TicketTypeModel, self).specification
        specification.extend([
            {
                'key': 'content_oid',
                'type': ObjectId,
                'default': None
            },
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
                'key': 'day',
                'type': int,
                'default': (lambda: 1)
            },
            {
                'key': 'price',
                'type': int,
                'default': None
            },
            {
                'key': 'enabled',
                'type': bool,
                'default': (lambda: True)
            },
        ])
        return specification
