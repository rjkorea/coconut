# -*- coding: utf-8 -*-

from handlers import index, a, v1

url_patterns = [
    (r'/', index.IndexHandler),
    (r'/ping/?', index.PingHandler),
    (r'/test?', index.TestHandler),
    (r'/test/(?P<oid>[^\/]+)/?', index.TestHandler),
    
    # admin
    (r'/a/auth/register/?', a.auth.RegisterHandler),
    (r'/a/auth/login/?', a.auth.LoginHandler),
    (r'/a/admins/?', a.admin.AdminListHandler),
    (r'/a/invitation/?', a.invitation.InvitationPostHandler),
    (r'/a/invitation/(?P<_id>[^\/]+)/?', a.invitation.InvitationHandler),
	(r'/a/invitations/?', a.invitation.InvitationListHandler),
    (r'/a/notification/(?P<_id>[^\/]+)/?', a.notification.NotificationHandler),
    (r'/a/notifications/?', a.notification.NotificationListHandler),

	# v1
	(r'/v1/invitation/submit/?', v1.invitation.SubmitHandler),
    (r'/v1/admins/?', v1.invitation.AdminListHandler)
]

