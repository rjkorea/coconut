# -*- coding: utf-8 -*-

from bson import ObjectId

from enum import Enum
from models.base import BaseModel


class NotificationModel(BaseModel):
    MONGO_COLLECTION = 'notification'

    def __init__(self, *args, **kwargs):
        super(NotificationModel, self).__init__(*args, **kwargs)

    @property
    def specification(self):
        specification = super(NotificationModel, self).specification
        specification.extend([
            {
                'key': 'admin_oid',
                'type': ObjectId,
                'default': None
            },
            {
                'key': 'message',
                'type': str,
                'default': None
            },
            {
                'key': 'type',
                'type': str,
                'default': None
            },
            {
                'key': 'read',
                'type': bool,
                'default': (lambda: False)
            },
            {
                'key': 'enabled',
                'type': bool,
                'default': (lambda: True)
            },
            {
                'key': 'data',
                'type': dict,
                'default': None
            }
        ])
        return specification
