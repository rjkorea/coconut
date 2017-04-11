# -*- coding: utf-8 -*-

from datetime import datetime
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


class TicketOrderModel(BaseModel):
    MONGO_COLLECTION = 'ticket_order'

    def __init__(self, *args, **kwargs):
        super(TicketOrderModel, self).__init__(*args, **kwargs)

    @property
    def specification(self):
        specification = super(TicketOrderModel, self).specification
        specification.extend([
            {
                'key': 'user_oid',
                'type': ObjectId,
                'default': None
            },
            {
                'key': 'ticket_type_oid',
                'type': ObjectId,
                'default': None
            },
            {
                'key': 'parent_oid',
                'type': ObjectId,
                'default': None
            },
            {
                'key': 'qty',
                'type': int,
                'default': None
            },
            {
                'key': 'receiver',
                'type': dict,
                'default': None
            },
            {
                'key': 'fee',
                'type': dict,
                'default': None
            },
            {
                'key': 'expiry_date',
                'type': datetime,
                'default': None
            },
            {
                'key': 'enabled',
                'type': bool,
                'default': (lambda: True)
            },
        ])
        return specification


class TicketModel(BaseModel):
    MONGO_COLLECTION = 'ticket'
    STATUS = ('pend', 'send', 'register', 'use')

    def __init__(self, *args, **kwargs):
        super(TicketModel, self).__init__(*args, **kwargs)

    @property
    def specification(self):
        specification = super(TicketModel, self).specification
        specification.extend([
            {
                'key': 'user_oid',
                'type': ObjectId,
                'default': None
            },
            {
                'key': 'ticket_order_oid',
                'type': ObjectId,
                'default': None
            },
            {
                'key': 'day',
                'type': int,
                'default': (lambda: 1)
            },
            {
                'key': 'status',
                'type': str,
                'default': (lambda: 'pend')
            },
            {
                'key': 'entered_at',
                'type': datetime,
                'default': None
            },
            {
                'key': 'enabled',
                'type': bool,
                'default': (lambda: True)
            },
        ])
        return specification
