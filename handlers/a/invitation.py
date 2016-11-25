# -*- coding: utf-8 -*-

from bson import ObjectId

from tornado.web import HTTPError

from common.decorators import admin_auth_async, parse_argument

from handlers.base import JsonHandler
from models.invitation import InvitationModel


class InvitationHandler(JsonHandler):
    # @admin_auth_async
    async def post(self, *args, **kwargs):
        mobile_number = self.json_decoded_body.get('mobile_number', None)
        if not mobile_number or len(mobile_number) == 0:
            raise HTTPError(400, 'invalid mobile_number')
        duplicated_invitation = await InvitationModel.find_one({'mobile_number': mobile_number})
        if duplicated_invitation:
            raise HTTPError(400, 'duplicated invitation')
        name = self.json_decoded_body.get('name', None)
        if not name or len(name) == 0:
            raise HTTPError(400, 'invalid name')
        birthday = self.json_decoded_body.get('birthday', None)
        if not birthday or len(birthday) == 0:
            raise HTTPError(400, 'invalid birthday')
        email = self.json_decoded_body.get('email', None)
        if not email or len(email) == 0:
            raise HTTPError(400, 'invalid email')
        gender = self.json_decoded_body.get('gender', None)
        if not gender or len(gender) == 0:
            raise HTTPError(400, 'invalid gender(male or female)')
        type = self.json_decoded_body.get('type', None)
        if not type or len(type) == 0:
            raise HTTPError(400, 'invalid type')
        invitation = InvitationModel(raw_data=dict(
            mobile_number=mobile_number,
            name=name,
            birthday=birthday,
            email=email,
            gender=gender,
            type=type
        ))
        await invitation.insert()
        self.response['data'] = invitation.data
        self.write_json()

    # @admin_auth_async
    async def put(self, *args, **kwargs):
        oid = self.json_decoded_body.pop('oid', None)
        if not oid or len(oid) == 0:
            raise HTTPError(400, 'invalid oid')
        invitation = await InvitationModel.find_one({'_id': ObjectId(oid)})
        if not invitation:
            raise HTTPError(400, 'not exist oid')
        query = {
            '_id': ObjectId(oid)
        }
        document = {
            '$set': self.json_decoded_body
        }
        self.response['data'] = await InvitationModel.update(query, document)
        self.write_json()


class InvitationListHandler(JsonHandler):
    # @admin_auth_async
    @parse_argument([('start', int, 0), ('size', int, 10), ])
    async def get(self, *args, **kwargs):
        parsed_args = kwargs.get('parsed_args')
        result = await InvitationModel.find(skip=parsed_args['start'], limit=parsed_args['size'])
        self.response['data'] = result 
        self.write_json()
