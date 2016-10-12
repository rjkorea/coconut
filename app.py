# -*- coding: utf-8 -*-


from tornado.log import logging

from tornado import web, ioloop, httpserver
from tornado.options import parse_command_line

from urls import url_patterns


class APIApplication(web.Application):
    def __init__(self, *args, **kwargs):
        config = kwargs.get('config', None)
        parse_command_line()
        super(APIApplication, self).__init__(url_patterns, **config['application'])


def main():
    import settings
    config = settings.settings()
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s:%(name)s:%(module)s %(message)s')
    logger = logging.getLogger(config['application']['name'])
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
