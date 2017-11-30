# -*- coding: utf-8 -*-

import logging
from common.utils import Singleton
from iamport import Iamport


class IamportService(Singleton):
    def __new__(cls, *args, **kwargs):
        _instance = super(IamportService, cls).__new__(cls, *args)
        config = kwargs.pop('config', None)
        if config:
            _instance.client = Iamport(imp_key=config['api_key'], imp_secret=config['api_secret'])
            logging.info('connected: %s' % _instance.client)
        return _instance
