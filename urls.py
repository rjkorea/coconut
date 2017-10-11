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
    (r'/a/dashboard/(?P<_id>[^\/]+)/?', a.dashboard.DashboardContentHandler),

    (r'/a/companies/?', a.company.CompanyListHandler),
    (r'/a/company/(?P<_id>[^\/]+)/?', a.company.CompanyHandler),
    (r'/a/company/?', a.company.CompanyHandler),

    (r'/a/admins/?', a.admin.AdminListHandler),
    (r'/a/admin/(?P<_id>[^\/]+)/?', a.admin.AdminHandler),
    (r'/a/admin/?', a.admin.AdminHandler),
    (r'/a/admin/(?P<_id>[^\/]+)/password/?', a.admin.AdminPasswordHandler),

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
    (r'/a/ticket/order/(?P<_id>[^\/]+)/send/?', a.ticket.TicketOrderSendHandler),
    (r'/a/ticket/order/(?P<_id>[^\/]+)/serial_number_list/?', a.ticket.TicketOrderSerialNumberList),

    (r'/a/tickets/?', a.ticket.TicketListHandler),
    (r'/a/ticket/(?P<_id>[^\/]+)/?', a.ticket.TicketHandler),
    (r'/a/ticket/(?P<_id>[^\/]+)/register/user/?', a.ticket.TicketRegisterUserHandler),
    (r'/a/ticket/?', a.ticket.TicketHandler),
    (r'/a/ticket/(?P<_id>[^\/]+)/cancel/?', a.ticket.TicketCancelHandler),
    (r'/a/ticket/(?P<_id>[^\/]+)/sms/send/?', a.ticket.TicketSmsSendHandler),


    (r'/a/places/?', a.place.PlaceListHandler),
    (r'/a/place/(?P<_id>[^\/]+)/?', a.place.PlaceHandler),
    (r'/a/place/?', a.place.PlaceHandler),
    (r'/a/places/stats/?', a.place.PlaceStatsHandler),

    (r'/a/qnas/?', a.qna.QnaListHandler),
    (r'/a/qna/(?P<_id>[^\/]+)/?', a.qna.QnaHandler),
    (r'/a/qna/?', a.qna.QnaHandler),

    (r'/a/countries/?', a.util.CountryListHandler),

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

    (r'/w/user/?', w.user.UserHandler),
    (r'/w/user/me/?', w.user.UserMeHandler),
    (r'/w/user/me/password?', w.user.UserMePasswordHandler),

    (r'/w/user/(?P<_id>[^\/]+)/new/password?', w.user.UserNewPasswordHandler),
    (r'/w/user/(?P<_id>[^\/]+)/auth/password?', w.user.UserAuthPasswordHandler),

    (r'/w/content/(?P<_id>[^\/]+)/?', w.content.ContentHandler),
    (r'/w/countries/?', w.util.CountryListHandler),

    (r'/w/ticket/orders/?', w.ticket.TicketOrderListHandler),
    (r'/w/ticket/order/(?P<_id>[^\/]+)/tickets/unused?', w.ticket.TicketUnusedListHandler),
    (r'/w/ticket/order/(?P<_id>[^\/]+)/tickets/used?', w.ticket.TicketUsedListHandler),
    (r'/w/ticket/(?P<_id>[^\/]+)/register/?', w.ticket.TicketRegisterHandler),
    (r'/w/ticket/(?P<_id>[^\/]+)/cancel/?', w.ticket.TicketCancelHandler),
    (r'/w/ticket/send/?', w.ticket.TicketSendHandler),
    (r'/w/ticket/send/batch/?', w.ticket.TicketSendBatchHandler),
    (r'/w/tickets/me/?', w.ticket.TicketListMeHandler),
    (r'/w/tickets/?', w.ticket.TicketListHandler),
    (r'/w/ticket/logs/?', w.ticket.TicketLogsHandler),

    (r'/w/qnas/?', w.qna.QnaListHandler),

    (r'/w/ticket/order/(?P<slug>[^\/]+)/?', w.ticket.TicketOrderSlugHandler),
    (r'/w/ticket/sn/(?P<serial_number>[^\/]+)/register?', w.ticket.TicketSerialNumberRegisterHandler),

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
