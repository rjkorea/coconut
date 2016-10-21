# -*- coding: utf-8 -*-

from models.base import BaseModel


class TestModel(BaseModel):
    MONGO_COLLECTION = 'test'

    def __init__(self, *args, **kwargs):
        super(TestModel, self).__init__(*args, **kwargs)

    @property
    def specification(self):
        specification = super(TestModel, self).specification
        specification.extend([
            {
                'key': 'name',
                'type': str,
                'default': None
            },
        ])
        return specification
