# -*- coding: utf-8 -8-


import os
import collections
from tornado.log import logging


_settings = dict(
    application=dict(
        name='coconut',
        env='live',
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
    mongodb = dict(
        host='11.0.1.90',
        port=27017,
        db='coconut'
    ),
    nexmo = dict(
        api_key='7968a1e2', 
        api_secret='a45366ce5d7a295c'
    ),
    host=dict(
        protocol='https',
        host='host.tkit.me',
        port=443
    ),
    web=dict(
        name='citron',
        host='i.tkit.me',
        port=80,
    ),
    tweb=dict(
        name='tomato',
        protocol='https',
        host='tkit.me',
        port=443,
    ),
    iamport=dict(
        api_key='4335180923213950',
        api_secret='8PJ0Bmp6JLDTBITQ281p2BuM5jJ0FpWOeGOQ2eWMZAGBizrkHtKK4ewaygadG72VORLR5IE5ikHBT8WA'
    ),
    aws=dict(
        access_key='AKIAJRLZGNWWWHRYRG7Q',
        secret_key='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',
        res_bucket='res.tkit.me',
        cloudfront='d3gdb0v1epkb6b.cloudfront.net'
    ),
    slack=dict(
        oauth_access_token='xoxp-24065128659-73904001223-457101199316-939af9f7bd0df067a789032615d2ad8f'
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
