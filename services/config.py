# -*- coding: utf-8 -*-

import logging
from common.utils import Singleton
import settings

class ConfigService(Singleton):
    def __new__(cls, *args, **kwargs):
        _instance = super(ConfigService, cls).__new__(cls, *args)
        config = kwargs.pop('config', None)
        if config:
            _instance.client = config
            logging.info('connected: %s' % _instance.client)
        return _instance
