# -*- coding: utf-8 -*-

import logging
from common.utils import Singleton
import boto3


class S3Service(Singleton):
    def __new__(cls, *args, **kwargs):
        _instance = super(S3Service, cls).__new__(cls, *args)
        config = kwargs.pop('config', None)
        if config:
            _instance.client = boto3.client('s3', aws_access_key_id=config['access_key'], aws_secret_access_key=config['secret_key'])
            logging.info('connected: %s' % _instance.client)
        return _instance
