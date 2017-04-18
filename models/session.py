# -*- coding: utf-8 -*-

from bson import ObjectId

from models.base import BaseModel


class AdminSessionModel(BaseModel):
    MONGO_COLLECTION = 'admin_session'

    def __init__(self, *args, **kwargs):
        super(AdminSessionModel, self).__init__(*args, **kwargs)

    @property
    def specification(self):
        specification = super(AdminSessionModel, self).specification
        specification.extend([
            {
                'key': 'admin_oid',
                'type': ObjectId,
                'default': None
            },
        ])
        return specification


class UserSessionModel(BaseModel):
    MONGO_COLLECTION = 'user_session'

    def __init__(self, *args, **kwargs):
        super(UserSessionModel, self).__init__(*args, **kwargs)

    @property
    def specification(self):
        specification = super(UserSessionModel, self).specification
        specification.extend([
            {
                'key': 'user_oid',
                'type': ObjectId,
                'default': None
            },
        ])
        return specification
