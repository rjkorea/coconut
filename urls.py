# -*- coding: utf-8 -*-


from handlers import index

url_patterns = [
    (r'/', index.IndexHandler),
    (r'/ping/?', index.PingHandler),
    (r'/test?', index.TestHandler),
    (r'/test/(?P<oid>[^\/]+)/?', index.TestHandler),
]

