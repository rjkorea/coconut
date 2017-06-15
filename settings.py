# -*- coding: utf-8 -8-


import os
import collections
from tornado.log import logging


_settings = dict(
    application=dict(
        name='coconut',
        host='api.tkit.me',
        port=9100,
        debug=False,
        autoreload=False,
        log=dict(
            level=logging.DEBUG,
            format='%(asctime)s %(levelname)s:%(name)s:%(module)s %(message)s'
        ),
        mobile = dict(
            ipad_id='582d37225f54714def85effb'
        )
    ),
    mongodb=dict(
        host='localhost',
        port=27017,
        db='coconut'
    ),
    nexmo=dict(
        api_key='7968a1e2',
        api_secret='a45366ce5d7a295c'
    ),
    web=dict(
        name='cherry',
        host='i.tkit.me',
        port=80,
    )
)




def settings():
    def update(original, local):
        for k, v in iter(local.items()):
            if isinstance(v, collections.Mapping):
                original[k].update(v)
            else:
                original[k] = v
        return original

    if os.path.isfile('settings_local.py'):
        import settings_local
        update(_settings, settings_local._settings)
        print(_settings)

    return _settings
