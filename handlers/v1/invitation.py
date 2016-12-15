# -*- coding: utf-8 -*

from tornado.web import HTTPError

from common.decorators import parse_argument, app_auth_async

from handlers.base import JsonHandler, WSHandler
from models.invitation import InvitationModel
from models.admin import AdminModel
from models.notification import NotificationModel


class SubmitHandler(JsonHandler):
    @app_auth_async
    async def put(self, *args, **kwargs):
        desk_number = self.json_decoded_body.get('desk_number', None)
        if not isinstance(desk_number, int):
            raise HTTPError(400, 'invalid desk_number')
        mobile_number = self.json_decoded_body.get('mobile_number', None)
        if not mobile_number or len(mobile_number) == 0:
            raise HTTPError(400, 'invalid mobile_number(+821022223333)')
        target_admin = await AdminModel.find_one({'desk_number': desk_number})
        if not target_admin:
            raise HTTPError(400, 'not exist desk number')
        query = {
        	'mobile_number': mobile_number
        }
        invitation = await InvitationModel.find_one(query)
        if not invitation:
            raise HTTPError(400, 'not exist mobile number')
        # save notification
        notification = NotificationModel(raw_data=dict(
            admin_oid=target_admin['_id'],
            type='request_auth',
            message='requested %s' % invitation['mobile_number'],
            data=invitation
        ))
        await notification.insert()
        ws_data = dict(
            admin_oid=str(target_admin['_id']),
            _id=str(invitation['_id']),
            name=invitation['name'],
            mobile_number=invitation['mobile_number'],
            assignee=invitation['assignee'],
            type=invitation['type'],
            fee=invitation['fee'],
            gender=invitation['gender'],
            email=invitation['email'],
            group=invitation['group'],
            entered=invitation['entered'],
            birthday=invitation['birthday'])
        WSHandler.write_to_clients(ws_data)
        self.response['data'] = invitation
        self.write_json()


class AdminListHandler(JsonHandler):
    @app_auth_async
    @parse_argument([('start', int, 0), ('size', int, 10), ])
    async def get(self, *args, **kwargs):
        parsed_args = kwargs.get('parsed_args')
        result = await AdminModel.find(skip=parsed_args['start'], limit=parsed_args['size'])
        self.response['data'] = result 
        self.write_json()