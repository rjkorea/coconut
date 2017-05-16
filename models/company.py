# -*- coding: utf-8 -*-

from bson import ObjectId

from models.base import BaseModel


class CompanyModel(BaseModel):
    MONGO_COLLECTION = 'company'

    def __init__(self, *args, **kwargs):
        super(CompanyModel, self).__init__(*args, **kwargs)

    @property
    def specification(self):
        specification = super(CompanyModel, self).specification
        specification.extend([
            {
                'key': 'name',
                'type': str,
                'default': None
            },
            {
                'key': 'contact',
                'type': dict,
                'default': None
            },
            {
                'key': 'admin_oid',
                'type': ObjectId,
                'default': None
            },
            {
                'key': 'enabled',
                'type': bool,
                'default': (lambda: False)
            },
        ])
        return specification
