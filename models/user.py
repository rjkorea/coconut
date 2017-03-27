# -*- coding: utf-8 -*-

from common import hashers

from models.base import BaseModel


class UserModel(BaseModel):
    MONGO_COLLECTION = 'user'
    ROLE = ('user', 'broker')

    def __init__(self, *args, **kwargs):
        super(UserModel, self).__init__(*args, **kwargs)

    @property
    def specification(self):
        specification = super(UserModel, self).specification
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
                'key': 'mobile_number',
                'type': str,
                'default': None
            },
            {
                'key': 'password',
                'type': str,
                'default': None
            },
            {
                'key': 'gender',
                'type': str,
                'default': None
            },
            {
                'key': 'birthday',
                'type': str,
                'default': None
            },
            {
                'key': 'role',
                'type': list,
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