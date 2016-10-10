# -*- coding: utf-8 -*-


import logging

from tornado import web, ioloop, httpserver

from urls import url_patterns


class APIApplication(web.Application):
    def __init__(self, *args, **kwargs):
        config = kwargs.get('config', None)
        super(APIApplication, self).__init__(url_patterns, **config['application'])


def main():
    import settings
    config = settings.settings()
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger('coconut')
    try:
        app = APIApplication(config=config)
        server = httpserver.HTTPServer(app, xheaders=True)
        server.bind(config['application']['port'])
        server.start(1)
        logger.info('api start up on Tornado listen %d' % config['application']['port'])
        ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        logger.info('KeyboardInterrupt occured. Stopping instance')
        ioloop.IOLoop.instance().stop()


if __name__ == '__main__':
    main()
