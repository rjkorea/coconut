# -*- coding: utf-8 -*-

from handlers import index, a

url_patterns = [
    (r'/', index.IndexHandler),
    (r'/ping/?', index.PingHandler),
    (r'/test?', index.TestHandler),
    (r'/test/(?P<oid>[^\/]+)/?', index.TestHandler),
    
    # admin
    (r'/a/auth/register/?', a.auth.RegisterHandler),
    (r'/a/auth/login/?', a.auth.LoginHandler),
    (r'/a/admins/?', a.admin.AdminListHandler),
    (r'/a/invitation/?', a.invitation.InvitationHandler),
]

