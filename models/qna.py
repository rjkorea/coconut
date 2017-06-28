# -*- coding: utf-8 -*-

from bson import ObjectId

from models.base import BaseModel


class QnaModel(BaseModel):
    MONGO_COLLECTION = 'qna'

    def __init__(self, *args, **kwargs):
        super(QnaModel, self).__init__(*args, **kwargs)

    @property
    def specification(self):
        specification = super(QnaModel, self).specification
        specification.extend([
            {
                'key': 'admin_oid',
                'type': ObjectId,
                'default': None
            },
            {
                'key': 'content_oid',
                'type': ObjectId,
                'default': None
            },
            {
                'key': 'question',
                'type': str,
                'default': None
            },
            {
                'key': 'answer',
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
