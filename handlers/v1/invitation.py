# -*- coding: utf-8 -*

from tornado.web import HTTPError

from common.decorators import parse_argument

from handlers.base import JsonHandler
from models.invitation import InvitationModel
from models.admin import AdminModel


class SubmitHandler(JsonHandler):
    async def put(self, *args, **kwargs):
        admin_oid = self.json_decoded_body.get('admin_oid', None)
        if not admin_oid or len(admin_oid) == 0:
            raise HTTPError(400, 'invalid admin_oid')
        mobile_number = self.json_decoded_body.get('mobile_number', None)
        if not mobile_number or len(mobile_number) == 0:
            raise HTTPError(400, 'invalid mobile_number(+821022223333)')
        query = {
        	'mobile_number': mobile_number
        }
        result = await InvitationModel.find_one(query)
        self.response['data'] = result
        self.write_json()


class AdminListHandler(JsonHandler):
    @parse_argument([('start', int, 0), ('size', int, 10), ])
    async def get(self, *args, **kwargs):
        parsed_args = kwargs.get('parsed_args')
        result = await AdminModel.find(skip=parsed_args['start'], limit=parsed_args['size'])
        self.response['data'] = result 
        self.write_json()