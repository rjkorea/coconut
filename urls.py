# -*- coding: utf-8 -*-


from handlers import index

url_patterns = [
    (r'/', index.PingHandler),
]

