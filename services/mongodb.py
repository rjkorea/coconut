# -*- coding: utf-8 -*-

from common.utils import Singleton
from motor import MotorClient


class MongodbService(Singleton):
    def __new__(cls, *args, **kwargs):
        _instance = super(MongodbService, cls).__new__(cls, *args)
        config = kwargs.pop('config', None)
        if config:
            _instance.client = MotorClient(config['host'], config['port'])[config['db']]
        return _instance
