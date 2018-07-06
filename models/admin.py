# -*- coding: utf-8 -*-

from bson import ObjectId
from common import hashers

from models.base import BaseModel


class AdminModel(BaseModel):
    MONGO_COLLECTION = 'admin'
    ROLE = ('admin', 'host', 'super', 'staff', 'pro')

    def __init__(self, *args, **kwargs):
        super(AdminModel, self).__init__(*args, **kwargs)

    @property
    def specification(self):
        specification = super(AdminModel, self).specification
        specification.extend([
            {
                'key': 'name',
                'type': str,
                'default': None
            },
            {
                'key': 'email',
                'type': str,
                'default': None
            },
            {
                'key': 'password',
                'type': str,
                'default': None
            },
            {
                'key': 'mobile_number',
                'type': str,
                'default': None
            },
            {
                'key': 'tablet_code',
                'type': str,
                'default': None
            },
            {
                'key': 'role',
                'type': str,
                'default': None
            },
            {
                'key': 'company_oid',
                'type': ObjectId,
                'default': None
            },
            {
                'key': 'company',
                'type': str,
                'default': None
            },
            {
                'key': 'website',
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

    def check_password(self, password):
        return hashers.check_password(password, self.data.get('password', ''))

    def set_password(self, password):
        self.data['password'] = hashers.make_password(password)
