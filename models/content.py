# -*- coding: utf-8 -*-

from bson import ObjectId

from common import hashers

from models.base import BaseModel


class ContentModel(BaseModel):
    MONGO_COLLECTION = 'content'
    SHORT_ID_LENGTH = 7
    IMAGE_TYPE = ('logo', 'poster', 'og', 'extra_0', 'extra_1', 'extra_2', 'extra_3', 'extra_4')

    def __init__(self, *args, **kwargs):
        super(ContentModel, self).__init__(*args, **kwargs)

    @property
    def specification(self):
        specification = super(ContentModel, self).specification
        specification.extend([
            {
                'key': 'short_id',
                'type': str,
                'default': None
            },
            {
                'key': 'admin_oid',
                'type': ObjectId,
                'default': None
            },
            {
                'key': 'company_oid',
                'type': ObjectId,
                'default': None
            },
            {
                'key': 'name',
                'type': str,
                'default': None
            },
            {
                'key': 'desc',
                'type': str,
                'default': None
            },
            {
                'key': 'images',
                'type': list,
                'default': None
            },
            {
                'key': 'place',
                'type': dict,
                'default': None
            },
            {
                'key': 'tags',
                'type': list,
                'default': None
            },
            {
                'key': 'when',
                'type': dict,
                'default': None
            },
            {
                'key': 'sms',
                'type': dict,
                'default': None
            },
            {
                'key': 'notice',
                'type': dict,
                'default': None
            },
            {
                'key': 'host',
                'type': dict,
                'default': None
            },
            {
                'key': 'site_url',
                'type': str,
                'default': None
            },
            {
                'key': 'video_url',
                'type': str,
                'default': None
            },
            {
                'key': 'purchase_url',
                'type': str,
                'default': None
            },
            {
                'key': 'staff_auth_code',
                'type': str,
                'default': None
            },
            {
                'key': 'is_private',
                'type': bool,
                'default': (lambda: False)
            },
            {
                'key': 'comments',
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
