# -*- coding: utf-8 -*-

from bson import ObjectId

from models.base import BaseModel


class GroupModel(BaseModel):
    MONGO_COLLECTION = 'group'

    def __init__(self, *args, **kwargs):
        super(GroupModel, self).__init__(*args, **kwargs)

    @property
    def specification(self):
        specification = super(GroupModel, self).specification
        specification.extend([
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
                'key': 'qty',
                'type': int,
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
        ])
        return specification


class GroupTicketModel(BaseModel):
    MONGO_COLLECTION = 'group_ticket'

    def __init__(self, *args, **kwargs):
        super(GroupTicketModel, self).__init__(*args, **kwargs)

    @property
    def specification(self):
        specification = super(GroupTicketModel, self).specification
        specification.extend([
            {
                'key': 'content_oid',
                'type': ObjectId,
                'default': None
            },
            {
                'key': 'group_oid',
                'type': ObjectId,
                'default': None
            },
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
                'key': 'used',
                'type': bool,
                'default': (lambda: False)
            },
            {
                'key': 'enabled',
                'type': bool,
                'default': (lambda: True)
            },
        ])
        return specification
