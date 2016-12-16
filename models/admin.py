# -*- coding: utf-8 -*-

from common import hashers

from models.base import BaseModel


class AdminModel(BaseModel):
    MONGO_COLLECTION = 'admin'

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