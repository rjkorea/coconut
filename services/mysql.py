# -*- coding: utf-8 -*-

import logging
from common.utils import Singleton

import mysql.connector
from mysql.connector.connection import MySQLConnection
from mysql.connector import pooling


class MySQLService(Singleton):
    def __new__(cls, *args, **kwargs):
        _instance = super(MySQLService, cls).__new__(cls, *args)
        config = kwargs.pop('config', None)
        if config:
            _instance.client = mysql.connector.pooling.MySQLConnectionPool(
                pool_name='mysql_pool',
                pool_size=config['pool_size'],
                pool_reset_session=True,
                host=config['host'],
                port=config['port'],
                database=config['db'],
                user=config['user'],
                password=config['password'])
            logging.info('connected: %s, %s, %s', _instance.client, _instance.client.pool_name, _instance.client.pool_size)
            logging
        return _instance
