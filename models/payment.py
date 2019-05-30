# -*- coding: utf-8 -*-

from datetime import datetime
from bson import ObjectId
from enum import Enum

from models.base import BaseModel


class PaymentModel(BaseModel):
    MONGO_COLLECTION = 'payment'
    CURRENCY = ('KRW', 'USD')

    def __init__(self, *args, **kwargs):
        super(PaymentModel, self).__init__(*args, **kwargs)

    @property
    def specification(self):
        specification = super(PaymentModel, self).specification
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
                'key': 'status',
                'type': str,
                'default': None
            },
            {
                'key': 'ticket_oids',
                'type': list,
                'default': None
            },
            {
                'key': 'imp_uid',
                'type': str,
                'default': None
            },
            {
                'key': 'merchant_uid',
                'type': str,
                'default': None
            },
            {
                'key': 'currency',
                'type': str,
                'default': None
            },
            {
                'key': 'amount',
                'type': float,
                'default': None
            },
            {
                'key': 'info',
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
