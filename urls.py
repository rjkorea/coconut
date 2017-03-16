# -*- coding: utf-8 -*-

from handlers import index, a, v1, base

url_patterns = [
    (r'/', index.IndexHandler),
    (r'/ping/?', index.PingHandler),
    (r'/test/?', index.TestHandler),
    (r'/test/(?P<oid>[^\/]+)/?', index.TestHandler),
    (r'/testws/?', index.WSTestHandler),

    # admin
    (r'/a/auth/register/?', a.auth.RegisterHandler),
    (r'/a/auth/login/?', a.auth.LoginHandler),
    (r'/a/dashboard/?', a.dashboard.DashboardHandler),
    (r'/a/admins/?', a.admin.AdminListHandler),
    (r'/a/admin/(?P<_id>[^\/]+)/?', a.admin.AdminHandler),
    (r'/a/users/?', a.user.UserListHandler),
    (r'/a/user/(?P<_id>[^\/]+)/?', a.user.UserHandler),
    (r'/a/invitation/?', a.invitation.InvitationPostHandler),
    (r'/a/invitation/(?P<_id>[^\/]+)/?', a.invitation.InvitationHandler),
	(r'/a/invitations/?', a.invitation.InvitationListHandler),
    (r'/a/notification/(?P<_id>[^\/]+)/?', a.notification.NotificationHandler),
    (r'/a/notifications/?', a.notification.NotificationListHandler),

	# v1
	(r'/v1/invitation/submit/?', v1.invitation.SubmitHandler),
    (r'/v1/admins/?', v1.invitation.AdminListHandler),

    # web socket handler
    (r'/ws/?', base.WSHandler),
]
