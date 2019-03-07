# -*- coding: utf-8 -*-

import logging
from common.utils import Singleton
from slacker import Slacker


class SlackService(Singleton):
    def __new__(cls, *args, **kwargs):
        _instance = super(SlackService, cls).__new__(cls, *args)
        config = kwargs.pop('config', None)
        if config:
            _instance.client = Slacker(config['oauth_access_token'])
            logging.info('connected: %s' % _instance.client)
        return _instance
