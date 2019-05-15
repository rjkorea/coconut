# -*- coding: utf-8 -*-

from handlers import index, base, a, av2, v1, t, tw, w, v2, wpc, wm, q, d

url_patterns = [
    (r'/', index.IndexHandler),
    (r'/ping/?', index.PingHandler),
    (r'/test/?', index.TestHandler),
    (r'/test/(?P<oid>[^\/]+)/?', index.TestHandler),
    (r'/testws/?', index.WSTestHandler),
    (r'/test/web/hook/?', index.WebHookTestHandler),

    # admin
    (r'/a/auth/register/?', a.auth.RegisterHandler),
    (r'/a/auth/signup/personal/?', a.auth.SignupPersonalHandler),
    (r'/a/auth/signup/business/?', a.auth.SignupBusinessHandler),
    (r'/a/auth/login/?', a.auth.LoginHandler),
    (r'/a/dashboard/?', a.dashboard.DashboardHandler),
    (r'/a/dashboard/(?P<_id>[^\/]+)/?', a.dashboard.DashboardContentHandler),
    (r'/a/stats/(?P<_id>[^\/]+)/?', a.stats.StatsContentHandler),
    (r'/a/tim/matrix/ticket/order/(?P<_id>[^\/]+)/?', a.tim.MatrixTicketOrderHandler),
    (r'/a/tim/matrix/ticket/type/(?P<_id>[^\/]+)/?', a.tim.MatrixTicketTypeHandler),
    (r'/a/tim/report/(?P<_id>[^\/]+)/?', a.tim.ReportHandler),
    (r'/a/tim/analytics/(?P<_id>[^\/]+)/?', a.tim.AnalyticsHandler),
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
    (r'/a/user/init/(?P<_id>[^\/]+)/?', a.user.UserInitHandler),
    (r'/a/contents/?', a.content.ContentListHandler),
    (r'/a/content/(?P<_id>[^\/]+)/?', a.content.ContentHandler),
    (r'/a/content/?', a.content.ContentPostHandler),
    (r'/a/content/(?P<_id>[^\/]+)/image/(?P<type>[^\/]+)/?', a.content.ContentImageUploadHandler),
    (r'/a/content/(?P<_id>[^\/]+)/active/user/?', a.content.ContentActiveUserHandler),
    (r'/a/content/(?P<_id>[^\/]+)/group/?', a.group.GroupHandler),
    (r'/a/content/(?P<content_oid>[^\/]+)/group/(?P<group_oid>[^\/]+)/?', a.group.GroupHandler),
    (r'/a/content/(?P<_id>[^\/]+)/groups/?', a.group.GroupListHandler),
    (r'/a/content/(?P<content_oid>[^\/]+)/group/(?P<group_oid>[^\/]+)/sms/send/?', a.group.GroupSmsSendHandler),
    (r'/a/content/(?P<content_oid>[^\/]+)/group/(?P<group_oid>[^\/]+)/ticket/?', a.group.GroupTicketHandler),
    (r'/a/content/(?P<content_oid>[^\/]+)/group/(?P<group_oid>[^\/]+)/tickets/?', a.group.GroupTicketListHandler),
    (r'/a/content/(?P<content_oid>[^\/]+)/group/(?P<group_oid>[^\/]+)/ticket/(?P<ticket_oid>[^\/]+)/?', a.group.GroupTicketHandler),
    (r'/a/content/(?P<content_oid>[^\/]+)/group/(?P<group_oid>[^\/]+)/ticket/(?P<ticket_oid>[^\/]+)/reset/?', a.group.GroupTicketResetHandler),
    (r'/a/content/(?P<content_oid>[^\/]+)/group/(?P<group_oid>[^\/]+)/ticket/(?P<ticket_oid>[^\/]+)/sms/send/?', a.group.GroupTicketSmsSendHandler),
    (r'/a/content/(?P<content_oid>[^\/]+)/group/ticket/search?', a.group.SearchGroupTicketHandler),
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
    (r'/a/tickets/logs/?', a.ticket.TicketLogListHandler),
    (r'/a/ticket/log/(?P<_id>[^\/]+)/?', a.ticket.TicketLogHandler),
    (r'/a/tickets/entrance/?', a.ticket.TicketEntranceListHandler),
    (r'/a/ticket/(?P<_id>[^\/]+)/enter/?', a.ticket.TicketEnterUserHandler),
    (r'/a/places/?', a.place.PlaceListHandler),
    (r'/a/place/(?P<_id>[^\/]+)/?', a.place.PlaceHandler),
    (r'/a/place/?', a.place.PlaceHandler),
    (r'/a/places/stats/?', a.place.PlaceStatsHandler),
    (r'/a/qnas/?', a.qna.QnaListHandler),
    (r'/a/qna/(?P<_id>[^\/]+)/?', a.qna.QnaHandler),
    (r'/a/qna/?', a.qna.QnaHandler),
    (r'/a/countries/?', a.util.CountryListHandler),

    # admin v2
    (r'/a/v2/auth/email/find/verification/?', av2.auth.EmailFindVerificationHandler),
    (r'/a/v2/auth/email/find/verification/(?P<code>[^\/]+)/?', av2.auth.EmailFindVerificationHandler),
    (r'/a/v2/auth/password/reset/verification/?', av2.auth.PasswordResetVerificationHandler),
    (r'/a/v2/auth/password/reset/verification/(?P<code>[^\/]+)/?', av2.auth.PasswordResetVerificationHandler),
    (r'/a/v2/auth/password/reset/?', av2.auth.PasswordResetHandler),
    (r'/a/v2/content/?', av2.content.ContentPostHandler),
    (r'/a/v2/contents/?', av2.content.ContentListHandler),
    (r'/a/v2/content/(?P<_id>[^\/]+)/?', av2.content.ContentHandler),
    (r'/a/v2/content/(?P<_id>[^\/]+)/image/main/?', av2.content.ContentImageMainHandler),
    (r'/a/v2/content/(?P<_id>[^\/]+)/image/extra/?', av2.content.ContentImageExtraHandler),
    (r'/a/v2/content/(?P<_id>[^\/]+)/image/extra/(?P<number>[^\/]+)/?', av2.content.ContentImageExtraHandler),
    (r'/a/v2/ticket/type/?', av2.ticket.TicketTypeHandler),
    (r'/a/v2/ticket/type/(?P<_id>[^\/]+)/?', av2.ticket.TicketTypeHandler),
    (r'/a/v2/ticket/types/?', av2.ticket.TicketTypeListHandler),
    (r'/a/v2/ticket/type/(?P<_id>[^\/]+)/info?', av2.ticket.TicketTypeInfoHandler),
    (r'/a/v2/ticket/order/?', av2.ticket.TicketOrderHandler),
    (r'/a/v2/ticket/order/csv?', av2.ticket.TicketOrderCsvHandler),
    (r'/a/v2/ticket/orders/?', av2.ticket.TicketOrderListHandler),
    (r'/a/v2/tickets/?', av2.ticket.TicketListHandler),
    (r'/a/v2/ticket/history?', av2.ticket.TicketHistoryListHandler),

    # legacy api for admin
    (r'/a/invitation/?', a.invitation.InvitationPostHandler),
    (r'/a/invitation/(?P<_id>[^\/]+)/?', a.invitation.InvitationHandler),
    (r'/a/invitations/?', a.invitation.InvitationListHandler),
    (r'/a/notification/(?P<_id>[^\/]+)/?', a.notification.NotificationHandler),
    (r'/a/notifications/?', a.notification.NotificationListHandler),

    # v1
    # (r'/v1/invitation/submit/?', v1.invitation.SubmitHandler),
    # (r'/v1/admins/?', v1.invitation.AdminListHandler),

    # v2
    (r'/v2/auth/login/?', v2.auth.LoginHandler),
    (r'/v2/user/me/?', v2.user.UserMeHandler),

    # w
    (r'/w/auth/user/?', w.auth.UserHandler),
    (r'/w/auth/sms/send?', w.auth.SmsSendHandler),
    (r'/w/auth/sms/verify?', w.auth.SmsVerifyHandler),
    (r'/w/auth/register/?', w.auth.RegisterHandler),
    (r'/w/auth/login/?', w.auth.LoginHandler),
    (r'/w/auth/duplicated/?', w.auth.DuplicatedHandler),
    (r'/w/auth/autologin/?', w.auth.AutoLoginHandler),
    (r'/w/auth/autologin/(?P<_id>[^\/]+)/?', w.auth.AutoLoginHandler),
    (r'/w/user/?', w.user.UserHandler),
    (r'/w/user/me/?', w.user.UserMeHandler),
    (r'/w/user/me/password?', w.user.UserMePasswordHandler),
    (r'/w/user/me/image?', w.user.UserMeImageUploadHandler),
    (r'/w/user/(?P<_id>[^\/]+)/new/password?', w.user.UserNewPasswordHandler),
    (r'/w/user/(?P<_id>[^\/]+)/auth/password?', w.user.UserAuthPasswordHandler),
    (r'/w/autologin/?', w.user.AutoLoginHandler),
    (r'/w/autologin/(?P<_id>[^\/]+)/?', w.user.AutoLoginHandler),
    (r'/w/content/(?P<_id>[^\/]+)/?', w.content.ContentHandler),
    (r'/w/contents/?', w.content.ContentListHandler),
    (r'/w/countries/?', w.util.CountryListHandler),
    (r'/w/ticket/(?P<_id>[^\/]+)/me/register/validate?', w.ticket.TicketMeRegisterValidateHandler),
    (r'/w/ticket/(?P<_id>[^\/]+)/register/?', w.ticket.TicketRegisterHandler),
    (r'/w/ticket/(?P<_id>[^\/]+)/register/cancel/?', w.ticket.TicketRegisterCancelHandler),
    (r'/w/tickets/register/?', w.ticket.TicketMultiRegisterHandler),
    (r'/w/ticket/send/?', w.ticket.TicketSendHandler),
    (r'/w/ticket/send/users?', w.ticket.TicketSendUserListHandler),
    (r'/w/tickets/me/?', w.ticket.TicketListMeHandler),
    (r'/w/tickets/?', w.ticket.TicketListHandler),
    (r'/w/ticket/(?P<_id>[^\/]+)/detail?', w.ticket.TicketHandler),
    (r'/w/tickets/validate?', w.ticket.TicketValidateListHandler),
    (r'/w/ticket/logs/?', w.ticket.TicketLogsHandler),
    (r'/w/ticket/payment/?', w.ticket.TicketPaymentHandler),
    (r'/w/ticket/(?P<_id>[^\/]+)/payment/status/?', w.ticket.TicketPaymentStatusHandler),
    (r'/w/ticket/(?P<_id>[^\/]+)/payment/cancel/?', w.ticket.TicketPaymentCancelHandler),
    (r'/w/ticket/(?P<_id>[^\/]+)/payment/complete/?', w.ticket.TicketPaymentCompleteHandler),
    (r'/w/ticket/payment/update/?', w.ticket.TicketPaymentUpdateHandler),
    (r'/w/ticket/(?P<_id>[^\/]+)/enter/?', w.ticket.TicketEnterUserHandler),
    (r'/w/ticket/types/me/?', w.ticket.TicketTypeListMeHandler),
    (r'/w/ticket/type/(?P<_id>[^\/]+)/tickets/?', w.ticket.TicketTypeTicketListMeHandler),
    (r'/w/qnas/?', w.qna.QnaListHandler),
    (r'/w/ticket/order/(?P<slug>[^\/]+)/?', w.ticket.TicketOrderSlugHandler),
    (r'/w/ticket/sn/(?P<serial_number>[^\/]+)/register/?', w.ticket.TicketSerialNumberRegisterHandler),
    (r'/w/payment/?', w.payment.PaymentHandler),
    (r'/w/payments/?', w.payment.PaymentListHandler),
    (r'/w/payment/success/?', w.payment.PaymentSuccessHandler),
    (r'/w/payment/fail/?', w.payment.PaymentFailHandler),

    # /w/pc
    (r'/w/pc/contents/?', wpc.content.ContentListHandler),
    (r'/w/pc/content/(?P<_id>[^\/]+)/?', wpc.content.ContentHandler),
    (r'/w/pc/sns/?', wpc.content.SnsContentListHandler),
    (r'/w/pc/countries/?', wpc.user.CountryListHandler),
    (r'/w/pc/sms/link/send/?', wpc.content.SendSmsBuyLinkHandler),

    # /w/m
    (r'/w/m/countries/?', wm.user.CountryListHandler),
    (r'/w/m/user/?', wm.user.UserHandler),
    (r'/w/m/user/me/?', wm.user.UserMeHandler),
    (r'/w/m/user/register/?', wm.user.UserRegisterHandler),
    (r'/w/m/user/(?P<_id>[^\/]+)/new/password?', wm.user.UserNewPasswordHandler),
    (r'/w/m/user/(?P<_id>[^\/]+)/auth/password?', wm.user.UserAuthPasswordHandler),
    (r'/w/m/autologin/?', wm.user.AutoLoginHandler),
    (r'/w/m/autologin/(?P<_id>[^\/]+)/?', wm.user.AutoLoginHandler),
    (r'/w/m/contents/?', wm.content.ContentListHandler),
    (r'/w/m/content/(?P<_id>[^\/]+)/?', wm.content.ContentHandler),
    (r'/w/m/contents/me?', wm.content.ContentListMeHandler),
    (r'/w/m/sns/?', wm.content.SnsContentListHandler),
    (r'/w/m/content/(?P<_id>[^\/]+)/ticket/orders?', wm.ticket.TicketOrderListHandler),
    (r'/w/m/ticket/send?', wm.ticket.TicketSendHandler),

    # t (tablet)
    (r'/t/host/?', t.admin.AdminHandler),
    (r'/t/contents/?', t.content.ContentListHandler),
    (r'/t/content/(?P<_id>[^\/]+)/?', t.content.ContentHandler),
    (r'/t/dashboard/(?P<_id>[^\/]+)/?', t.dashboard.DashboardHandler),
    (r'/t/auth/?', t.auth.AuthHandler),
    (r'/t/countries/?', t.util.CountryListHandler),

    # tw (tablet web)
    (r'/tw/auth/login/?', tw.auth.LoginHandler),
    (r'/tw/contents/?', tw.contents.ContentsListHandler),
    (r'/tw/contents/(?P<_id>[^\/]+)/?', tw.contents.ContentsHandler),
    (r'/tw/countries/?', tw.utils.CountryListHandler),

    # q (qrcode app)
    (r'/q/auth/login/?', q.auth.LoginHandler),
    (r'/q/contents/me/?', q.content.ContentListMeHandler),
    (r'/q/content/(?P<_id>[^\/]+)/tickets/?', q.ticket.TicketListUserHandler),
    (r'/q/ticket/(?P<_id>[^\/]+)/enter/?', q.ticket.TicketEnterUserHandler),
    (r'/q/user/(?P<_id>[^\/]+)/?', q.user.UserHandler),

    # debug
    (r'/d/user/(?P<_id>[^\/]+)/?', d.user.UserHandler),

    # web socket handler
    (r'/ws/?', base.WSHandler),
]
