# -*- coding: utf-8 -*

from tornado.web import HTTPError

from handlers.base import JsonHandler
from models.invitation import InvitationModel


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
