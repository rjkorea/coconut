# -*- coding: utf-8 -*-

from datetime import datetime
from bson import ObjectId
from enum import Enum

from common import hashers

from models.base import BaseModel


class TicketTypeModel(BaseModel):
    MONGO_COLLECTION = 'ticket_type'
    TICKET_TYPE = ('general', 'network')
    COLORS = ('tkit-mint', 'tkit-coral', 'hangang-blue', 'ultra-bora', 'mustard-norang')
    MAX = 200

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
                'key': 'admin_oid',
                'type': ObjectId,
                'default': None
            },
            {
                'key': 'type',
                'type': str,
                'default': None
            },
            {
                'key': 'name',
                'type': str,
                'default': None
            },
            {
                'key': 'desc',
                'type': dict,
                'default': None
            },
            {
                'key': 'sales_date',
                'type': dict,
                'default': None
            },
            {
                'key': 'fpfg',
                'type': dict,
                'default': None
            },
            {
                'key': 'price',
                'type': int,
                'default': None
            },
            {
                'key': 'color',
                'type': dict,
                'default': (lambda: {'name': 'tkit-mint', 'value': '#62aab8'})
            },
            {
                'key': 'duplicated_registration',
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


class TicketOrderModel(BaseModel):
    MONGO_COLLECTION = 'ticket_order'

    def __init__(self, *args, **kwargs):
        super(TicketOrderModel, self).__init__(*args, **kwargs)

    @property
    def specification(self):
        specification = super(TicketOrderModel, self).specification
        specification.extend([
            {
                'key': 'admin_oid',
                'type': ObjectId,
                'default': None
            },
            {
                'key': 'user_oid',
                'type': ObjectId,
                'default': None
            },
            {
                'key': 'content_oid',
                'type': ObjectId,
                'default': None
            },
            {
                'key': 'ticket_type_oid',
                'type': ObjectId,
                'default': None
            },
            {
                'key': 'type',
                'type': str,
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
                'key': 'slug',
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


class TicketModel(BaseModel):
    MONGO_COLLECTION = 'ticket'
    SERIAL_NUMBER_LENGTH = 7
    Status = Enum('Status', 'pend send register pay use cancel')

    def __init__(self, *args, **kwargs):
        super(TicketModel, self).__init__(*args, **kwargs)

    @property
    def specification(self):
        specification = super(TicketModel, self).specification
        specification.extend([
            {
                'key': 'send_user_oid',
                'type': ObjectId,
                'default': None
            },
            {
                'key': 'receive_user_oid',
                'type': ObjectId,
                'default': None
            },
            {
                'key': 'history_send_user_oids',
                'type': list,
                'default': None
            },
            {
                'key': 'ticket_type_oid',
                'type': ObjectId,
                'default': None
            },
            {
                'key': 'ticket_order_oid',
                'type': ObjectId,
                'default': None
            },
            {
                'key': 'content_oid',
                'type': ObjectId,
                'default': None
            },
            {
                'key': 'type',
                'type': str,
                'default': None
            },
            {
                'key': 'price',
                'type': int,
                'default': None
            },
            {
                'key': 'days',
                'type': dict,
                'default': None
            },
            {
                'key': 'status',
                'type': str,
                'default': (lambda: 'pend')
            },
            {
                'key': 'serial_number',
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


class TicketLogModel(BaseModel):
    MONGO_COLLECTION = 'ticket_log'
    Status = Enum('Status', 'pend send register pay use cancel')

    def __init__(self, *args, **kwargs):
        super(TicketLogModel, self).__init__(*args, **kwargs)

    @property
    def specification(self):
        specification = super(TicketLogModel, self).specification
        specification.extend([
            {
                'key': 'action',
                'type': str,
                'default': None
            },
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
                'key': 'send_user_oid',
                'type': ObjectId,
                'default': None
            },
            {
                'key': 'receive_user_oid',
                'type': ObjectId,
                'default': None
            },
            {
                'key': 'ticket_oids',
                'type': list,
                'default': None
            },
        ])
        return specification


class TicketPlaceModel(BaseModel):
    MONGO_COLLECTION = 'ticket_place'
    TYPE = ('area', 'seat', 'site')

    def __init__(self, *args, **kwargs):
        super(TicketPlaceModel, self).__init__(*args, **kwargs)

    @property
    def specification(self):
        specification = super(TicketPlaceModel, self).specification
        specification.extend([
            {
                'key': 'type',
                'type': str,
                'default': (lambda: 'area')
            },
            {
                'key': 'serial',
                'type': dict,
                'default': None
            },
            {
                'key': 'enabled',
                'type': bool,
                'default': (lambda: True)
            },
            {
                'key': 'ticket_oid',
                'type': ObjectId,
                'default': None
            },
            {
                'key': 'content_oid',
                'type': ObjectId,
                'default': None
            },
            {
                'key': 'admin_oid',
                'type': ObjectId,
                'default': None
            },
        ])
        return specification
