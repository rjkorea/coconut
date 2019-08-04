# -*- coding: utf-8 -*-


from bson import ObjectId

from tornado.web import HTTPError

from common.decorators import admin_auth_async, parse_argument

from handlers.base import JsonHandler
from models.content import ContentModel
from models.ticket import TicketModel, TicketTypeModel
from models.user import UserModel
from models.admin import AdminModel
from models.target import TargetModel

from services.lms import LmsService


class TargetHandler(JsonHandler):
    @admin_auth_async
    @parse_argument([('content_oid', str, None), ('ticket_type_oids', str, None), ('status', str, 'send,register,pay,use,cancel')])
    async def get(self, *args, **kwargs):
        parsed_args = kwargs.get('parsed_args')
        content_oid = parsed_args['content_oid']
        if not content_oid or len(content_oid) != 24:
            raise HTTPError(400, self.set_error(1, 'invalid content_oid'))
        content = await ContentModel.find_one({'_id': ObjectId(content_oid)})
        if not content:
            raise HTTPError(400, self.set_error(2, 'not exist content'))
        ticket_type_oids = parsed_args['ticket_type_oids']
        if ticket_type_oids:
            ticket_type_oids = [{'ticket_type_oid': ObjectId(t)} for t in ticket_type_oids.split(',')]
        status = parsed_args['status'].split(',')
        if status:
            status = [{'status': s} for s in status]
        pipeline = [
            {
                '$match': {
                    'content_oid': ObjectId(content_oid)
                }
            },
            {
                '$match': {
                    '$or': status
                }
            },
            {
                '$lookup': {
                    'from': 'user',
                    'localField': 'receive_user_oid',
                    'foreignField': '_id',
                    'as': 'receive_user'
                }
            },
            {
                '$group': {
                    '_id': {
                        'name': '$receive_user.name',
                        'mobile_country_code': '$receive_user.mobile.country_code',
                        'mobile_number': '$receive_user.mobile.number'
                    }
                }
            },
            {
                '$group': {
                    '_id': None,
                    'count': {
                        '$sum': 1
                    }
                }
            }
        ]
        if ticket_type_oids:
            pipeline[0]['$match']['$or'] = ticket_type_oids
        aggs = await TicketModel.aggregate(pipeline, -1)
        if aggs:
            self.response['count'] = aggs[0]['count']
        else:
            self.response['count'] = 0
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class TargetSendHandler(JsonHandler):
    @admin_auth_async
    async def put(self, *args, **kwargs):
        content_oid = self.json_decoded_body.get('content_oid', None)
        if not content_oid or len(content_oid) != 24:
            raise HTTPError(400, self.set_error(1, 'invalid content_oid'))
        content = await ContentModel.find_one({'_id': ObjectId(content_oid)})
        if not content:
            raise HTTPError(400, self.set_error(2, 'not exist content'))
        ticket_type_oids = self.json_decoded_body.get('ticket_type_oids', None)
        if ticket_type_oids:
            pipe_ticket_type_oids = [{'ticket_type_oid': ObjectId(t)} for t in ticket_type_oids]
        status = self.json_decoded_body.get('status', None)
        if status:
            pipe_status = [{'status': s} for s in status]
        pipeline = [
            {
                '$match': {
                    'content_oid': ObjectId(content_oid)
                }
            },
            {
                '$match': {
                    '$or': pipe_status
                }
            },
            {
                '$lookup': {
                    'from': 'user',
                    'localField': 'receive_user_oid',
                    'foreignField': '_id',
                    'as': 'receive_user'
                }
            },
            {
                '$group': {
                    '_id': {
                        'name': '$receive_user.name',
                        'mobile_country_code': '$receive_user.mobile.country_code',
                        'mobile_number': '$receive_user.mobile.number'
                    }
                }
            }
        ]
        if pipe_ticket_type_oids:
            pipeline[0]['$match']['$or'] = pipe_ticket_type_oids
        aggs = await TicketModel.aggregate(pipeline, -1)
        sms = self.json_decoded_body.get('sms', None)
        success_count = 0
        for a in aggs:
            if a['_id']['mobile_country_code'][0] == '82':
                res = LmsService().send(a['_id']['mobile_number'][0], sms['title'], sms['message'])
                if 'result_code' in res and res['result_code'] == '200' and res['result_message'] == 'OK':
                    success_count = success_count + 1
        target = TargetModel(raw_data=dict(
            admin_oid=self.current_user['_id'],
            type='lms',
            content_oid=content['_id'],
            ticket_type_oids=ticket_type_oids,
            status=status,
            sms=sms,
            count=len(aggs),
            success_count=success_count
        ))
        await target.insert()
        self.response['data'] = dict(
            count=len(aggs),
            success=success_count
        )
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class TargetListHandler(JsonHandler):
    @admin_auth_async
    @parse_argument([('start', int, 0), ('size', int, 10)])
    async def get(self, *args, **kwargs):
        parsed_args = kwargs.get('parsed_args')
        count = await TargetModel.count()
        targets = await TargetModel.find(skip=parsed_args['start'], limit=parsed_args['size'])
        for t in targets:
            t['admin'] = await AdminModel.get_id(t['admin_oid'], fields=[('name'), ('last_name')])
            t['content'] = await ContentModel.get_id(t['content_oid'], fields=[('name')])
            t['ticket_type'] = await TicketTypeModel.get_id(ObjectId(t['ticket_type_oids'][0]), fields=[('name')])
            t.pop('admin_oid')
            t.pop('content_oid')
            t.pop('ticket_type_oids')
        self.response['data'] = targets
        self.response['count'] = count
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()