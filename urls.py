# -*- coding: utf-8 -*-

from handlers import index, base, a, v1, t, w

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

    (r'/a/companies/?', a.company.CompanyListHandler),
    (r'/a/company/(?P<_id>[^\/]+)/?', a.company.CompanyHandler),
    (r'/a/company/?', a.company.CompanyHandler),

    (r'/a/admins/?', a.admin.AdminListHandler),
    (r'/a/admin/(?P<_id>[^\/]+)/?', a.admin.AdminHandler),
    (r'/a/admin/?', a.admin.AdminHandler),

    (r'/a/users/?', a.user.UserListHandler),
    (r'/a/user/(?P<_id>[^\/]+)/?', a.user.UserHandler),
    (r'/a/user/?', a.user.UserHandler),

    (r'/a/contents/?', a.content.ContentListHandler),
    (r'/a/content/(?P<_id>[^\/]+)/?', a.content.ContentHandler),
    (r'/a/content/?', a.content.ContentHandler),

    (r'/a/ticket/types/?', a.ticket.TicketTypeListHandler),
    (r'/a/ticket/type/(?P<_id>[^\/]+)/?', a.ticket.TicketTypeHandler),
    (r'/a/ticket/type/?', a.ticket.TicketTypeHandler),

    (r'/a/ticket/orders/?', a.ticket.TicketOrderListHandler),
    (r'/a/ticket/order/(?P<_id>[^\/]+)/?', a.ticket.TicketOrderHandler),
    (r'/a/ticket/order/?', a.ticket.TicketOrderHandler),
    (r'/a/ticket/order/(?P<_id>[^\/]+)/send?', a.ticket.TicketOrderSendHandler),

    (r'/a/tickets/?', a.ticket.TicketListHandler),
    (r'/a/ticket/(?P<_id>[^\/]+)/?', a.ticket.TicketHandler),
    (r'/a/ticket/?', a.ticket.TicketHandler),

    # legacy api for admin
    (r'/a/invitation/?', a.invitation.InvitationPostHandler),
    (r'/a/invitation/(?P<_id>[^\/]+)/?', a.invitation.InvitationHandler),
	(r'/a/invitations/?', a.invitation.InvitationListHandler),

    (r'/a/notification/(?P<_id>[^\/]+)/?', a.notification.NotificationHandler),
    (r'/a/notifications/?', a.notification.NotificationListHandler),

	# v1
	# (r'/v1/invitation/submit/?', v1.invitation.SubmitHandler),
    # (r'/v1/admins/?', v1.invitation.AdminListHandler),

    # w
    (r'/w/auth/login/?', w.auth.LoginHandler),

    (r'/w/content/(?P<_id>[^\/]+)/?', w.content.ContentHandler),
    (r'/w/countries/?', w.util.CountryListHandler),

    (r'/w/ticket/orders/?', w.ticket.TicketOrderListHandler),
    (r'/w/tickets/?', w.ticket.TicketListHandler),

    # t (tablet)
    (r'/t/host/?', t.admin.AdminHandler),
    (r'/t/contents/?', t.content.ContentListHandler),
    (r'/t/content/(?P<_id>[^\/]+)/?', t.content.ContentHandler),
    (r'/t/dashboard/(?P<_id>[^\/]+)/?', t.dashboard.DashboardHandler),
    (r'/t/auth/?', t.auth.AuthHandler),
    (r'/t/countries/?', t.util.CountryListHandler),

    # web socket handler
    (r'/ws/?', base.WSHandler),
]
