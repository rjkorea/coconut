# -*- coding: utf-8 -*-


from tornado.log import logging

from tornado import web, ioloop, httpserver
from tornado.options import parse_command_line

from urls import url_patterns

from services.mongodb import MongodbService
from services.sms import NexmoService
from services.iamport import IamportService
from services.s3 import S3Service
from services.cloudfront import CloudfrontService
from services.slack import SlackService
# from services.mysql import MySQLService
from services.kakaotalk import KakaotalkService
from services.lms import LmsService
from services.config import ConfigService


class APIApplication(web.Application):
    def __init__(self, *args, **kwargs):
        config = kwargs.get('config', None)
        parse_command_line()
        super(APIApplication, self).__init__(url_patterns, **config['application'])


def main():
    import settings
    config = settings.settings()
    logging.basicConfig(level=config['application']['log']['level'], format=config['application']['log']['format'])
    logger = logging.getLogger(config['application']['name'])
    try:
        app = APIApplication(config=config)
        server = httpserver.HTTPServer(app, xheaders=True)
        server.bind(config['application']['port'])
        server.start(1)
        logger.info('api start up on Tornado listen %d' % config['application']['port'])
        MongodbService(config=config['mongodb'])
        # MySQLService(config=config['mysql'])
        NexmoService(config=config['nexmo'])
        IamportService(config=config['iamport'])
        S3Service(config=config['aws'])
        CloudfrontService(config=config['aws'])
        SlackService(config=config['slack'])
        KakaotalkService()
        LmsService()
        ConfigService(config=config)
        ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        logger.info('KeyboardInterrupt occured. Stopping instance')
        ioloop.IOLoop.instance().stop()


if __name__ == '__main__':
    main()
