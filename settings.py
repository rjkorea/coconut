# -*- coding: utf-8 -8-


from tornado.log import logging


_settings = dict(
    application=dict(
        name='coconut',
        port=5100,
        debug=True,
        autoreload=True,
        log=dict(
            level=logging.DEBUG,
            format='%(asctime)s %(levelname)s:%(name)s:%(module)s %(message)s'
        )
    ),
    mongodb=dict(
        host='localhost',
        port=27017,
        db='coconut'
    )
)


def settings():
    return _settings
