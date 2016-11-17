# -*- coding: utf-8 -*-

from models.base import BaseModel


class InvitationModel(BaseModel):
    MONGO_COLLECTION = 'invitation'

    def __init__(self, *args, **kwargs):
        super(InvitationModel, self).__init__(*args, **kwargs)

    @property
    def specification(self):
        specification = super(InvitationModel, self).specification
        specification.extend([
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
                'key': 'birthday',
                'type': str,
                'default': None
            },
            {
                'key': 'email',
                'type': str,
                'default': None
            },
            {
                'key': 'gender',
                'type': str,
                'default': None
            },
            {
                'key': 'type',
                'type': str,
                'default': None
            },
            {
                'key': 'entered',
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
