# -*- coding: utf-8 -*-

from bson import ObjectId
from datetime import datetime

from models.base import BaseModel


class VerificationModel(BaseModel):
    MONGO_COLLECTION = 'verification'

    def __init__(self, *args, **kwargs):
        super(VerificationModel, self).__init__(*args, **kwargs)

    @property
    def specification(self):
        specification = super(VerificationModel, self).specification
        specification.extend([
            {
                'key': 'code',
                'type': str,
                'default': None
            },
            {
                'key': 'mobile_number',
                'type': str,
                'default': None
            },
            {
                'key': 'expired_at',
                'type': datetime,
                'default': datetime.utcnow
            },
            {
                'key': 'enabled',
                'type': bool,
                'default': (lambda: True)
            }
        ])
        return specification
