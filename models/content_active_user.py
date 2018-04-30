# -*- coding: utf-8 -*-

from bson import ObjectId

from models.base import BaseModel


class ContentActiveUser(BaseModel):
    MONGO_COLLECTION = 'content_active_user'

    def __init__(self, *args, **kwargs):
        super(ContentActiveUser, self).__init__(*args, **kwargs)

    @property
    def specification(self):
        specification = super(ContentActiveUser, self).specification
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
            }
        ])
        return specification
