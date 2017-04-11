# -*- coding: utf-8 -*-

import logging
from common.utils import Singleton
import nexmo


class NexmoService(Singleton):
    def __new__(cls, *args, **kwargs):
        _instance = super(NexmoService, cls).__new__(cls, *args)
        config = kwargs.pop('config', None)
        if config:
            _instance.client = nexmo.Client(key=config['api_key'], secret=config['api_secret'])
            logging.info('connected: %s' % _instance.client)
        return _instance
