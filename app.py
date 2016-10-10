# -*- coding: utf-8 -*-


import logging

from tornado import web, ioloop, httpserver
from urls import url_patterns


class APIApplication(web.Application):
    def __init__(self, *args, **kwargs):
        config = dict()
        super(APIApplication, self).__init__(url_patterns, **config)
        pass

def main():
    #import settings
    #config = settings.settings()
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger('coconut')
    try:
        app = APIApplication()
        server = httpserver.HTTPServer(app, xheaders=True)
        server.bind(8888)
        server.start(1)
        logger.info('api start up on Tornado listen %d' % 8888)
        ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        logger.info('KeyboardInterrupt occured. Stopping instance')
        ioloop.IOLoop.instance().stop()


if __name__ == '__main__':
    main()
