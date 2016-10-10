# -*- coding: utf-8 -*-


from handlers import index

url_patterns = [
    (r'/', index.IndexHandler),
    (r'/ping', index.PingHandler),
]

