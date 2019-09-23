# -*- coding: utf-8 -*-

from bson import ObjectId
from datetime import datetime, timedelta

from tornado.web import HTTPError

from common import hashers
from common.decorators import user_auth_async, parse_argument

from handlers.base import JsonHandler
from models.user import UserModel, UserSendHistoryModel
from models.content import ContentModel
from models.ticket import TicketOrderModel, TicketTypeModel, TicketModel, TicketLogModel

from models import create_user

from services.iamport import IamportService
from services.kakaotalk import KakaotalkService


class TicketMeRegisterValidateHandler(JsonHandler):
    @user_auth_async
    async def get(self, *args, **kwargs):
        _id = kwargs.get('_id', None)
        if not _id or len(_id) != 24:
            raise HTTPError(400, 'invalid _id')
        ticket = await TicketModel.find_one({'_id': ObjectId(_id)})
        if not ticket:
            raise HTTPError(400, 'not exist ticket')
        if ticket['status'] == TicketModel.Status.register.name:
            raise HTTPError(400, 'registered ticket can\'t register')
        if ticket['status'] == TicketModel.Status.use.name:
            raise HTTPError(400, 'used ticket can\'t register')
        if ticket['status'] == TicketModel.Status.cancel.name:
            raise HTTPError(400, 'canceled ticket can\'t register')
        if ticket['status'] == TicketModel.Status.pay.name:
            raise HTTPError(400, 'paid ticket can\'t register')
        ticket_type = await TicketTypeModel.get_id(ticket['ticket_type_oid'])
        query = {
            '$and': [
                {'enabled': True},
                {'ticket_type_oid': ticket['ticket_type_oid']},
                {
                    '$or': [
                        {'status': TicketModel.Status.register.name},
                        {'status': TicketModel.Status.pay.name},
                        {'status': TicketModel.Status.use.name}
                    ]
                }
            ]
        }
        sales_count = await TicketModel.count(query)
        if sales_count >= ticket_type['fpfg']['limit']:
            raise HTTPError(400, 'excceed register limit')
        q = {
            '$and': [
                {'ticket_type_oid': ticket['ticket_type_oid']},
                {'content_oid': ticket['content_oid']},
                {'receive_user_oid': self.current_user['_id']},
                {
                    '$or': [
                        {'status': TicketModel.Status.register.name},
                        {'status': TicketModel.Status.pay.name},
                        {'status': TicketModel.Status.use.name},
                    ]
                }
            ]
        }
        exist_ticket = await TicketModel.find_one(q)
        if exist_ticket:
            ticket_type = await TicketTypeModel.get_id(exist_ticket['ticket_type_oid'])
            if 'duplicated_registration' not in ticket_type or not ticket_type['duplicated_registration']:
                raise HTTPError(400, 'Already registered ticket type on this content')
        self.response['data'] = dict(validate=True)
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class TicketRegisterHandler(JsonHandler):
    @user_auth_async
    async def put(self, *args, **kwargs):
        _id = kwargs.get('_id', None)
        if not _id or len(_id) != 24:
            raise HTTPError(400, 'invalid _id')
        ticket = await TicketModel.find_one({'_id': ObjectId(_id)})
        if not ticket:
            raise HTTPError(400, 'not exist ticket')
        if ticket['receive_user_oid'] != self.current_user['_id']:
            raise HTTPError(400, 'this is not your ticket')
        if ticket['status'] == TicketModel.Status.register.name:
            raise HTTPError(400, 'registered ticket can\'t register')
        if ticket['status'] == TicketModel.Status.use.name:
            raise HTTPError(400, 'used ticket can\'t register')
        if ticket['status'] == TicketModel.Status.cancel.name:
            raise HTTPError(400, 'canceled ticket can\'t register')
        if ticket['status'] == TicketModel.Status.pay.name:
            raise HTTPError(400, 'paid ticket can\'t register')
        ticket_type = await TicketTypeModel.get_id(ticket['ticket_type_oid'])
        query = {
            '$and': [
                {'enabled': True},
                {'ticket_type_oid': ticket['ticket_type_oid']},
                {
                    '$or': [
                        {'status': TicketModel.Status.register.name},
                        {'status': TicketModel.Status.pay.name},
                        {'status': TicketModel.Status.use.name}
                    ]
                }
            ]
        }
        sales_count = await TicketModel.count(query)
        if sales_count >= ticket_type['fpfg']['limit']:
            raise HTTPError(400, 'excceed register limit')
        q = {
            '$and': [
                {'ticket_type_oid': ticket['ticket_type_oid']},
                {'content_oid': ticket['content_oid']},
                {'receive_user_oid': self.current_user['_id']},
                {
                    '$or': [
                        {'status': TicketModel.Status.register.name},
                        {'status': TicketModel.Status.pay.name},
                        {'status': TicketModel.Status.use.name},
                    ]
                }
            ]
        }
        exist_ticket = await TicketModel.find_one(q)
        if exist_ticket:
            ticket_type = await TicketTypeModel.get_id(exist_ticket['ticket_type_oid'])
            if 'duplicated_registration' not in ticket_type or not ticket_type['duplicated_registration']:
                raise HTTPError(400, 'Already registered ticket type on this content')
        email = self.json_decoded_body.get('email', None)
        birthday = self.json_decoded_body.get('birthday', None)
        gender = self.json_decoded_body.get('gender', None)
        if email and birthday and gender:
            user = await UserModel.update({'_id': self.current_user['_id']}, {'$set': {'email': email, 'birthday': birthday, 'gender': gender}})
        query = {
            '_id': ObjectId(_id)
        }
        document = {
            '$set': {
                'receive_user_oid': self.current_user['_id'],
                'status': TicketModel.Status.register.name,
                'updated_at': datetime.utcnow()
            }
        }
        result = await TicketModel.update(query, document)
        if result['nModified'] == 1:
            await TicketTypeModel.update({'_id': ticket['ticket_type_oid']}, {'$inc': {'fpfg.now': 1}})
        self.response['data'] = result
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class TicketMultiRegisterHandler(JsonHandler):
    @user_auth_async
    async def put(self, *args, **kwargs):
        ticket_oids = self.json_decoded_body.get('ticket_oids', None)
        if not ticket_oids or len(ticket_oids) == 0:
            raise HTTPError(400, 'invalid ticket_oids')
        email = self.json_decoded_body.get('email', None)
        birthday = self.json_decoded_body.get('birthday', None)
        gender = self.json_decoded_body.get('gender', None)
        if email and birthday and gender:
            user = await UserModel.update({'_id': self.current_user['_id']}, {'$set': {'email': email, 'birthday': birthday, 'gender': gender}})
        query = {
            '_id': {
                '$in': []
            }
        }
        for t in ticket_oids:
            query['_id']['$in'].append(ObjectId(t))
        document = {
            '$set': {
                'receive_user_oid': self.current_user['_id'],
                'status': TicketModel.Status.register.name,
                'updated_at': datetime.utcnow()
            }
        }
        self.response['data'] = await TicketModel.update(query, document, False, True)
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class TicketSendHandler(JsonHandler):
    @user_auth_async
    async def put(self, *args, **kwargs):
        ticket_oids = self.json_decoded_body.get('ticket_oids', None)
        if not ticket_oids or not isinstance(ticket_oids, list):
            raise HTTPError(400, 'invalid ticket_oids')
        ticket_types = list()
        for t_oid in ticket_oids:
            ticket = await TicketModel.get_id(ObjectId(t_oid) ,fields=[('ticket_type_oid')])
            ticket_type = await TicketTypeModel.get_id(ticket['ticket_type_oid'], fields=[('disabled_send', 'name')])
            ticket_types.append(ticket_type)
            if 'disabled_send' in ticket_type and ticket_type['disabled_send']:
                raise HTTPError(400, 'Cannot send ticket')
        for t_oid in ticket_oids:
            ticket = await TicketModel.find_one({'_id': ObjectId(t_oid)})
            if ticket and ticket['receive_user_oid'] != self.current_user['_id']:
                raise HTTPError(400, 'is not your ticket')
        receive_user = self.json_decoded_body.get('receive_user', None)
        if not receive_user or not isinstance(receive_user, dict):
            raise HTTPError(400, 'invalid receive_user')
        if receive_user['mobile']['country_code'] == '82' and not receive_user['mobile']['number'].startswith('010'):
            raise HTTPError(400, 'invalid Korea mobile number')
        receive_user = await create_user(receive_user)
        if self.current_user['_id'] == receive_user['_id']:
            raise HTTPError(400, 'cannot send to myself')
        query = {'$or': []}
        for t_oid in ticket_oids:
            query['$or'].append({'_id': ObjectId(t_oid)})
        document = {
            '$set': {
                'status': TicketModel.Status.send.name,
                'send_user_oid': self.current_user['_id'],
                'receive_user_oid': receive_user['_id'],
                'updated_at': datetime.utcnow()
            },
            '$addToSet': {
                'history_send_user_oids': self.current_user['_id']
            }
        }
        self.response['data'] = await TicketModel.update(query, document, False, True)
        toids = [ObjectId(oid) for oid in ticket_oids]
        tm = await TicketModel.get_id(ObjectId(ticket_oids[0]))
        ticket_log = TicketLogModel(raw_data=dict(
            action=TicketLogModel.Status.send.name,
            send_user_oid=self.current_user['_id'],
            receive_user_oid=receive_user['_id'],
            content_oid=tm['content_oid'],
            ticket_oids=toids
        ))
        await ticket_log.insert()
        user_send_history = await UserSendHistoryModel.find_one({'user_oid': self.current_user['_id'], 'mobile.country_code': receive_user['mobile']['country_code'], 'mobile.number': receive_user['mobile']['number']})
        if user_send_history:
            await UserSendHistoryModel.update({'_id': user_send_history['_id']}, {'$set': {'updated_at': datetime.utcnow()}}, False, False)
        else:
            user_send_history = UserSendHistoryModel(raw_data=dict(
                user_oid=self.current_user['_id'],
                name=receive_user['name'],
                mobile=receive_user['mobile']
            ))
            await user_send_history.insert()
        if receive_user['mobile']['country_code'] == '82':
            content = await ContentModel.find_one({'_id': tm['content_oid']}, fields=[('name'), ('when'), ('place.name'), ('band_place'), ('short_id')])
            others = dict()
            for t in ticket_types:
                if t['name'] in others:
                    others[t['name']] = others[t['name']] + 1
                else:
                    others[t['name']] = 1
            main_ticket = others.popitem()
            if others:
                others = ', '.join(['%s <%d장>'%(k,v) for k,v in others.items()])
            else:
                others = ' '
            KakaotalkService().tmp032(
                receive_user['mobile']['number'],
                receive_user['name'],
                self.current_user['name'],
                content['name'],
                main_ticket[0],
                main_ticket[1],
                others,
                content['short_id']
            )
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class TicketTypesSendHandler(JsonHandler):
    @user_auth_async
    async def put(self, *args, **kwargs):
        ticket_types = self.json_decoded_body.get('ticket_types', None)
        if not ticket_types or not isinstance(ticket_types, list):
            raise HTTPError(400, 'invalid ticket_types')
        ticket_oids = list()
        for tt in ticket_types:
            if tt[1] > 200:
                raise HTTPError(400, 'Maxium qty is 200 on system')
            tickets = await TicketModel.find({'ticket_type_oid': ObjectId(tt[0]), 'receive_user_oid': self.current_user['_id'], 'status': TicketModel.Status.send.name}, fields=[('_id')], skip=0, limit=tt[1])
            if tt[1] > len(tickets):
                raise HTTPError(400, 'unavailable qty: %d' % tt[1])
            for t in tickets:
                ticket_oids.append(str(t['_id']))
        ticket_types = list()
        for t_oid in ticket_oids:
            ticket = await TicketModel.get_id(ObjectId(t_oid) ,fields=[('ticket_type_oid')])
            ticket_type = await TicketTypeModel.get_id(ticket['ticket_type_oid'], fields=[('disabled_send'), ('name')])
            ticket_types.append(ticket_type)
            if 'disabled_send' in ticket_type and ticket_type['disabled_send']:
                raise HTTPError(400, 'Cannot send ticket')
        for t_oid in ticket_oids:
            ticket = await TicketModel.find_one({'_id': ObjectId(t_oid)})
            if ticket and ticket['receive_user_oid'] != self.current_user['_id']:
                raise HTTPError(400, 'is not your ticket')
        receive_user = self.json_decoded_body.get('receive_user', None)
        if not receive_user or not isinstance(receive_user, dict):
            raise HTTPError(400, 'invalid receive_user')
        if receive_user['mobile']['country_code'] == '82' and not receive_user['mobile']['number'].startswith('010'):
            raise HTTPError(400, 'invalid Korea mobile number')
        receive_user = await create_user(receive_user)
        if self.current_user['_id'] == receive_user['_id']:
            raise HTTPError(400, 'cannot send to myself')
        query = {'$or': []}
        for t_oid in ticket_oids:
            query['$or'].append({'_id': ObjectId(t_oid)})
        document = {
            '$set': {
                'status': TicketModel.Status.send.name,
                'send_user_oid': self.current_user['_id'],
                'receive_user_oid': receive_user['_id'],
                'updated_at': datetime.utcnow()
            },
            '$addToSet': {
                'history_send_user_oids': self.current_user['_id']
            }
        }
        self.response['data'] = await TicketModel.update(query, document, False, True)
        toids = [ObjectId(oid) for oid in ticket_oids]
        tm = await TicketModel.get_id(ObjectId(ticket_oids[0]))
        ticket_log = TicketLogModel(raw_data=dict(
            action=TicketLogModel.Status.send.name,
            send_user_oid=self.current_user['_id'],
            receive_user_oid=receive_user['_id'],
            content_oid=tm['content_oid'],
            ticket_oids=toids
        ))
        await ticket_log.insert()
        user_send_history = await UserSendHistoryModel.find_one({'user_oid': self.current_user['_id'], 'mobile.country_code': receive_user['mobile']['country_code'], 'mobile.number': receive_user['mobile']['number']})
        if user_send_history:
            await UserSendHistoryModel.update({'_id': user_send_history['_id']}, {'$set': {'updated_at': datetime.utcnow()}}, False, False)
        else:
            user_send_history = UserSendHistoryModel(raw_data=dict(
                user_oid=self.current_user['_id'],
                name=receive_user['name'],
                mobile=receive_user['mobile']
            ))
            await user_send_history.insert()

        if receive_user['mobile']['country_code'] == '82':
            content = await ContentModel.find_one({'_id': tm['content_oid']}, fields=[('name'), ('when'), ('place.name'), ('band_place'), ('short_id')])
            others = dict()
            for t in ticket_types:
                if t['name'] in others:
                    others[t['name']] = others[t['name']] + 1
                else:
                    others[t['name']] = 1
            main_ticket = others.popitem()
            if others:
                others = ', '.join(['%s <%d장>'%(k,v) for k,v in others.items()])
            else:
                others = ' '
            KakaotalkService().tmp032(
                receive_user['mobile']['number'],
                receive_user['name'],
                self.current_user['name'],
                content['name'],
                main_ticket[0],
                main_ticket[1],
                others,
                content['short_id']
            )
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class TicketListMeHandler(JsonHandler):
    @user_auth_async
    @parse_argument([('start', int, 0), ('size', int, 10), ('content_oid', str, None)])
    async def get(self, *args, **kwargs):
        parsed_args = kwargs.get('parsed_args')
        q = {
            '$and': [
                {
                    'receive_user_oid': self.current_user['_id'],
                    'enabled': True
                },
                {
                    '$or': [
                        {'status': TicketModel.Status.register.name},
                        {'status': TicketModel.Status.pay.name},
                        {'status': TicketModel.Status.use.name},
                        {'status': TicketModel.Status.cancel.name}
                    ]
                }
            ]
        }
        if parsed_args['content_oid']:
            q['$and'][0]['content_oid'] = ObjectId(parsed_args['content_oid'])
        count = await TicketModel.count(query=q)
        result = await TicketModel.find(query=q, sort=[('updated_at', -1)], skip=parsed_args['start'], limit=parsed_args['size'])
        for res in result:
            res['ticket_type'] = await TicketTypeModel.get_id(res['ticket_type_oid'])
            res.pop('ticket_type_oid')
            res['ticket_order'] = await TicketOrderModel.get_id(res['ticket_order_oid'])
            res.pop('ticket_order_oid')
            res['content'] = await ContentModel.get_id(res['content_oid'])
            res.pop('content_oid')
            if 'send_user_oid'in res:
                res['send_user'] = await UserModel.get_id(res['send_user_oid'])
                res.pop('send_user_oid')
            if 'receive_user_oid'in res:
                res['receive_user'] = await UserModel.get_id(res['receive_user_oid'])
                res.pop('receive_user_oid')
        self.response['data'] = result
        self.response['count'] = count
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class TicketListHandler(JsonHandler):
    @user_auth_async
    @parse_argument([('start', int, 0), ('size', int, 10), ('content_oid', str, None), ('status', str, None)])
    async def get(self, *args, **kwargs):
        parsed_args = kwargs.get('parsed_args')
        q = {
            'receive_user_oid': self.current_user['_id'],
            'enabled': True,
            'status': {'$ne': TicketModel.Status.pend.name}
        }
        if parsed_args['content_oid']:
            q['content_oid'] = ObjectId(parsed_args['content_oid'])
        if parsed_args['status']:
            q['status'] = parsed_args['status']
        count = await TicketModel.count(query=q)
        result = await TicketModel.find(query=q, sort=[('status', 1), ('created_at', -1), ('price', 1)], skip=parsed_args['start'], limit=parsed_args['size'])
        for res in result:
            res['ticket_type'] = await TicketTypeModel.get_id(res['ticket_type_oid'])
            res['ticket_type']['sales'] = {
                'count': res['ticket_type']['fpfg']['now'],
                'limit': res['ticket_type']['fpfg']['limit']
            }
            res.pop('ticket_type_oid')
            res['content'] = await ContentModel.get_id(res['content_oid'], fields=[('name')])
            res.pop('content_oid')
        self.response['data'] = result
        self.response['count'] = count
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class TicketHandler(JsonHandler):
    @user_auth_async
    async def get(self, *args, **kwargs):
        ticket_oid = kwargs.get('_id', None)
        if not ticket_oid or len(ticket_oid) != 24:
            raise HTTPError(400, 'invalid ticket_oid')
        ticket = await TicketModel.get_id(ObjectId(ticket_oid))
        ticket['ticket_type'] = await TicketTypeModel.get_id(ticket['ticket_type_oid'])
        ticket.pop('ticket_type_oid')
        ticket['ticket_order'] = await TicketOrderModel.get_id(ticket['ticket_order_oid'])
        ticket.pop('ticket_order_oid')
        ticket['content'] = await ContentModel.get_id(ticket['content_oid'])
        ticket.pop('content_oid')
        if 'send_user_oid'in ticket:
            ticket['send_user'] = await UserModel.get_id(ticket['send_user_oid'])
            ticket.pop('send_user_oid')
        if 'receive_user_oid'in ticket:
            ticket['receive_user'] = await UserModel.get_id(ticket['receive_user_oid'])
            ticket.pop('receive_user_oid')
        if 'history_send_user_oids' in ticket:
            ticket['history_send_users'] = list()
            for user_oid in ticket['history_send_user_oids']:
                user = await UserModel.get_id(user_oid, fields=[('name'), ('mobile'), ('last_name')])
                ticket['history_send_users'].append(user)
            ticket.pop('history_send_user_oids')
        self.response['data'] = ticket
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class TicketValidateListHandler(JsonHandler):
    @user_auth_async
    @parse_argument([('start', int, 0), ('size', int, 10), ('content_oid', str, None)])
    async def get(self, *args, **kwargs):
        parsed_args = kwargs.get('parsed_args')
        q = {
            'content_oid': ObjectId(parsed_args['content_oid']),
            'enabled': True,
            'sales_date.end': {
                '$gte': datetime.utcnow()
            }
        }
        ticket_types = await TicketTypeModel.find(query=q, fields=[('_id')], skip=0, limit=100)
        q = {
            'receive_user_oid': self.current_user['_id'],
            'enabled': True,
            'status': TicketModel.Status.send.name,
            'ticket_type_oid': {
                '$in': [ObjectId(tt['_id']) for tt in ticket_types]
            }
        }
        self.response['count'] = await TicketModel.count(query=q)
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class TicketOrderSlugHandler(JsonHandler):
    async def get(self, *args, **kwargs):
        slug = kwargs.get('slug', None)
        if not slug:
            raise HTTPError(400, 'invalid slug')
        res = await TicketOrderModel.find_one({'slug': slug})
        if not res:
            raise HTTPError(400, 'no exist ticket order')
        res['content'] = await ContentModel.get_id(res['content_oid'])
        res.pop('content_oid')
        res['ticket_type'] = await TicketTypeModel.get_id(res['ticket_type_oid'])
        res.pop('ticket_type_oid')
        self.response['data'] = res
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class TicketSerialNumberRegisterHandler(JsonHandler):
    async def put(self, *args, **kwargs):
        serial_number = kwargs.get('serial_number', None)
        if not serial_number or len(serial_number) != 7:
            raise HTTPError(400, 'invalid serial number')
        ticket = await TicketModel.find_one({'serial_number': serial_number})
        if not ticket:
            raise HTTPError(400, 'not exist serial number')
        if ticket['status'] == TicketModel.Status.register.name:
            raise HTTPError(400, 'registered ticket can\'t register')
        if ticket['status'] == TicketModel.Status.use.name:
            raise HTTPError(400, 'used ticket can\'t register')
        if ticket['status'] == TicketModel.Status.cancel.name:
            raise HTTPError(400, 'canceled ticket can\'t register')
        name = self.json_decoded_body.get('name', None)
        if not name:
            raise HTTPError(400, 'invalid name')
        mobile = self.json_decoded_body.get('mobile', None)
        if not mobile:
            raise HTTPError(400, 'invalid mobile number')
        user = await create_user(self.json_decoded_body)
        registered_user = await TicketModel.find_one({'content_oid': ticket['content_oid'], 'receive_user_oid': user['_id'], 'status': TicketModel.Status.register.name})
        if registered_user:
            raise HTTPError(400, 'already registered user')
        query = {
            '_id': ticket['_id'],
            'status': TicketModel.Status.pend.name
        }
        document = {
            '$set': {
                'receive_user_oid': user['_id'],
                'status': TicketModel.Status.register.name,
                'updated_at': datetime.utcnow()
            }
        }
        self.response['data'] = await TicketModel.update(query, document)
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class TicketSendUserListHandler(JsonHandler):
    @user_auth_async
    @parse_argument([('q', str, None), ('start', int, 0), ('size', int, 20)])
    async def get(self, *args, **kwargs):
        q = {
            'user_oid': self.current_user['_id'],
            'enabled': True
        }
        parsed_args = kwargs.get('parsed_args')
        if 'q' in parsed_args and parsed_args['q']:
            q['name'] = {
                '$regex': parsed_args['q']
            }
        count = await UserSendHistoryModel.count(query=q)
        history = await UserSendHistoryModel.find(query=q, fields={'mobile': True, 'name': True, 'updated_at': True}, sort=[('updated_at', -1)], skip=parsed_args['start'], limit=parsed_args['size'])
        self.response['count'] = count
        self.response['data'] = history
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class TicketLogsHandler(JsonHandler):
    @user_auth_async
    @parse_argument([('start', int, 0), ('size', int, 10), ('content_oid', str, None)])
    async def get(self, *args, **kwargs):
        parsed_args = kwargs.get('parsed_args')
        q = {
            'send_user_oid': self.current_user['_id'],
            'action': TicketLogModel.Status.send.name
        }
        if parsed_args['content_oid']:
            q['content_oid'] = ObjectId(parsed_args['content_oid'])
        count = await TicketLogModel.count(query=q)
        result = await TicketLogModel.find(query=q, skip=parsed_args['start'], limit=parsed_args['size'])
        for res in result:
            res['send_user'] = await UserModel.get_id(res['send_user_oid'], fields=[('name'), ('last_name'), ('mobile')])
            res.pop('send_user_oid')
            res['receive_user'] = await UserModel.get_id(res['receive_user_oid'], fields=[('name'), ('last_name'), ('mobile')])
            res.pop('receive_user_oid')
            res['tickets'] = list()
            returnable_ticket_count = 0
            for oid in res['ticket_oids']:
                tm = await TicketModel.get_id(oid, fields=[('ticket_type_oid'), ('receive_user_oid'), ('status')])
                if tm['receive_user_oid'] == res['receive_user']['_id'] and tm['status'] == TicketModel.Status.send.name:
                    returnable_ticket_count = returnable_ticket_count + 1
                ttm = await TicketTypeModel.get_id(tm['ticket_type_oid'], fields=[('name'), ('desc')])
                res['tickets'].append(ttm)
            res.pop('ticket_oids')
            res['returnable_ticket_count'] = returnable_ticket_count
        self.response['data'] = result
        self.response['count'] = count
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class TicketLogReturnHandler(JsonHandler):
    @user_auth_async
    async def put(self, *args, **kwargs):
        _id = kwargs.get('_id', None)
        if not _id or len(_id) != 24:
            raise HTTPError(400, 'invalid ticket_log_oid')
        ticket_log = await TicketLogModel.get_id(ObjectId(_id))
        if not ticket_log:
            raise HTTPError(400, 'not exist ticket_log')
        if ticket_log['send_user_oid'] != self.current_user['_id']:
            raise HTTPError(400, 'this is not yours ticket log')
        for toid in ticket_log['ticket_oids']:
            tm = await TicketModel.get_id(toid, fields=[('receive_user_oid'), ('status')])
            if tm['receive_user_oid'] != ticket_log['receive_user_oid'] or tm['status'] != TicketModel.Status.send.name:
                raise HTTPError(400, 'already used ticket')
        q = {'$or': []}
        for t_oid in ticket_log['ticket_oids']:
            q['$or'].append({'_id': ObjectId(t_oid)})
        doc = {
            '$set': {
                'status': TicketModel.Status.send.name,
                'send_user_oid': ticket_log['receive_user_oid'],
                'receive_user_oid': ticket_log['send_user_oid'],
                'updated_at': datetime.utcnow()
            },
            '$addToSet': {
                'history_send_user_oids': ticket_log['receive_user_oid']
            }
        }
        await TicketModel.update(q, doc, False, True)
        await TicketLogModel.update({'_id': ticket_log['_id']}, {'$set': {'status': 'return', 'returned_at': datetime.utcnow()}}, False, False)
        return_ticket_log = TicketLogModel(raw_data=dict(
            action='return',
            send_user_oid=ticket_log['receive_user_oid'],
            receive_user_oid=ticket_log['send_user_oid'],
            content_oid=ticket_log['content_oid'],
            ticket_oids=ticket_log['ticket_oids']
        ))
        await return_ticket_log.insert()
        receive_user = await UserModel.get_id(ticket_log['receive_user_oid'], fields=[('mobile'), ('name')])
        if receive_user['mobile']['country_code'] == '82':
            content = await ContentModel.find_one({'_id': ticket_log['content_oid']}, fields=[('name'), ('when'), ('place.name'), ('band_place'), ('short_id')])
            ticket = await TicketModel.get_id(ticket_log['ticket_oids'][0], fields=[('ticket_type_oid')])
            ticket_type = await TicketTypeModel.get_id(ticket['ticket_type_oid'], fields=[('name')])
            if 'band_place' not in content or not content['band_place']:
                KakaotalkService().tmp017(
                    receive_user['mobile']['number'],
                    receive_user['name'],
                    self.current_user['name'],
                    content['name'],
                    '%s - %s' % (datetime.strftime(content['when']['start'] + timedelta(hours=9), '%Y.%m.%d %a %H:%M'), datetime.strftime(content['when']['end'] + timedelta(hours=9), '%Y.%m.%d %a %H:%M')),
                    content['place']['name'],
                    ticket_type['name']
                )
            else:
                KakaotalkService().tmp017(
                    receive_user['mobile']['number'],
                    receive_user['name'],
                    self.current_user['name'],
                    content['name'],
                    '%s - %s' % (datetime.strftime(content['when']['start'] + timedelta(hours=9), '%Y.%m.%d %a %H:%M'), datetime.strftime(content['when']['end'] + timedelta(hours=9), '%Y.%m.%d %a %H:%M')),
                    content['band_place'],
                    ticket_type['name']
                )
        self.response['data'] = 'OK'
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class TicketPaymentHandler(JsonHandler):
    @user_auth_async
    @parse_argument([('imp_uid', str, None)])
    async def get(self, *args, **kwargs):
        parsed_args = kwargs.get('parsed_args')
        if 'imp_uid' not in parsed_args:
            raise HTTPError(400, 'invalid imp_uid')
        payment_result = IamportService().client.find(imp_uid=parsed_args['imp_uid'])
        ticket = await TicketModel.find_one({'_id': ObjectId(payment_result['merchant_uid'])})
        if not ticket:
            raise HTTPError(400, 'invalid payment')
        if ticket['price'] > 0:
            res = IamportService().client.is_paid(ticket['price'], merchant_uid=payment_result['merchant_uid'])
            if not res:
                raise HTTPError(400, 'invalid price')
        else:
            raise HTTPError(400, 'not exist fee')
        data = dict(
            imp_uid=payment_result['imp_uid'],
            merchant_uid=payment_result['merchant_uid'],
            name=payment_result['name'],
            currency=payment_result['currency'],
            amount=payment_result['amount'],
            status=payment_result['status'],
            paid_at=payment_result['paid_at'],
            receipt_url=payment_result['receipt_url'],
            pg_provier=payment_result['pg_provider'],
            pay_method=payment_result['pay_method'],
            apply_num=payment_result['apply_num'],
            buyer_name=payment_result['buyer_name'],
            buyer_tel=payment_result['buyer_tel'],
            buyer_email=payment_result['buyer_email'],
            card_name=payment_result['card_name'],
            card_code=payment_result['card_code'],
            card_quota=payment_result['card_quota'],
            pg_tid=payment_result['pg_tid'],
            user_agent=payment_result['user_agent'],
            cancel_amount=payment_result['cancel_amount'],
            cancel_reason=payment_result['cancel_reason'],
            cancelled_at=payment_result['cancelled_at'],
            cancel_receipt_urls=payment_result['cancel_receipt_urls'],
            cancel_history=payment_result['cancel_history'],
        )
        self.response['data'] = data
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class TicketPaymentStatusHandler(JsonHandler):
    @user_auth_async
    async def get(self, *args, **kwargs):
        _id = kwargs.get('_id', None)
        if not _id or len(_id) != 24:
            raise HTTPError(400, 'invalid ticket_oid')
        payment = IamportService().client.find(merchant_uid=_id)
        if payment == {}:
            raise HTTPError(400, 'not exist payment info')
        data = dict(
            imp_uid=payment['imp_uid'],
            merchant_uid=payment['merchant_uid'],
            name=payment['name'],
            currency=payment['currency'],
            amount=payment['amount'],
            status=payment['status'],
            paid_at=payment['paid_at'],
            receipt_url=payment['receipt_url'],
            pg_provier=payment['pg_provider'],
            pay_method=payment['pay_method'],
            apply_num=payment['apply_num'],
            buyer_name=payment['buyer_name'],
            buyer_tel=payment['buyer_tel'],
            buyer_email=payment['buyer_email'],
            card_name=payment['card_name'],
            card_code=payment['card_code'],
            card_quota=payment['card_quota'],
            pg_tid=payment['pg_tid'],
            user_agent=payment['user_agent'],
            cancel_amount=payment['cancel_amount'],
            cancel_reason=payment['cancel_reason'],
            cancelled_at=payment['cancelled_at'],
            cancel_receipt_urls=payment['cancel_receipt_urls'],
            cancel_history=payment['cancel_history'],
        )
        self.response['data'] = data
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class TicketPaymentCancelHandler(JsonHandler):
    async def put(self, *args, **kwargs):
        _id = kwargs.get('_id', None)
        if not _id or len(_id) != 24:
            raise HTTPError(400, 'invalid _id')
        reason = self.json_decoded_body.get('reason', None)
        if not reason:
            raise HTTPError(400, 'invalid reason')
        ticket = await TicketModel.get_id(ObjectId(_id))
        if not ticket:
            raise HTTPError(400, 'not exist ticket')
        try:
            response = IamportService().client.cancel(reason, merchant_uid=_id)
        except IamportService().client.ResponseError as e:
            raise HTTPError(e.code, e.message)
        if response['status'] == 'cancelled':
            query = {
                '_id': ObjectId(_id)
            }
            document = {
                '$set': {
                    'status': TicketModel.Status.cancel.name,
                    'updated_at': datetime.utcnow()
                }
            }
            result = await TicketModel.update(query, document, False, False)
            if result['nModified'] == 1:
                await TicketTypeModel.update({'_id': ticket['ticket_type_oid']}, {'$inc': {'fpfg.now': -1}})
        data = dict(
            name=response['name'],
            buyer_name=response['buyer_name'],
            buyer_tel=response['buyer_tel'],
            status=response['status'],
            imp_uid=response['imp_uid'],
            cancel_amount=response['cancel_amount'],
            cancel_reason=response['cancel_reason'],
            cancelled_at=response['cancelled_at'],
            cancel_receipt_urls=response['cancel_receipt_urls'],
            cancel_history=response['cancel_history']
        )
        self.response['data'] = data
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class TicketPaymentCompleteHandler(JsonHandler):
    async def put(self, *args, **kwargs):
        _id = kwargs.get('_id', None)
        if not _id or len(_id) != 24:
            raise HTTPError(400, 'invalid ticket_oid')
        ticket = await TicketModel.get_id(ObjectId(_id))
        if not ticket:
            raise HTTPError(400, 'not exsit ticket')
        payment = IamportService().client.find(merchant_uid=_id)
        if payment == {}:
            raise HTTPError(400, 'not exist payment info')
        if payment['status'] == 'paid':
            query = {
                '_id': ObjectId(_id),
                'status': TicketModel.Status.send.name
            }
            document = {
                '$set': {
                    'status': TicketModel.Status.pay.name,
                    'updated_at': datetime.utcnow()
                }
            }
            result = await TicketModel.update(query, document)
            if result['nModified'] == 1:
                await TicketTypeModel.update({'_id': ticket['ticket_type_oid']}, {'$inc': {'fpfg.now': 1}})
            self.response['data'] = result
            self.write_json()
        else:
            raise HTTPError(400, 'status is not paid on iamport')

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class TicketPaymentUpdateHandler(JsonHandler):
    async def post(self, *args, **kwargs):
        merchant_uid = self.json_decoded_body.get('merchant_uid', None)
        if not merchant_uid or len(merchant_uid) == 0:
            raise HTTPError(400, 'invalid merchant_uid')
        status = self.json_decoded_body.get('status', None)
        if not status or status != 'paid':
            raise HTTPError(400, 'invalid status')
        payment = IamportService().client.find(merchant_uid=merchant_uid)
        if payment == {}:
            raise HTTPError(400, 'not exist payment info')
        if payment['status'] == 'paid':
            ticket = await TicketModel.get_id(ObjectId(merchant_uid))
            if not ticket:
                raise HTTPError(400, 'not exist ticket')
            if ticket['status'] == TicketModel.Status.send.name:
                query = {
                    '_id': ObjectId(merchant_uid)
                }
                document = {
                    '$set': {
                        'status': TicketModel.Status.pay.name,
                        'updated_at': datetime.utcnow()
                    }
                }
                result = await TicketModel.update(query, document)
                if result['nModified'] == 1:
                    await TicketTypeModel.update({'_id': ticket['ticket_type_oid']}, {'$inc': {'fpfg.now': 1}})
                self.response['data'] = result
            elif ticket['status'] == TicketModel.Status.pay.name:
                self.response['data'] = {'message': 'Already updated pay of ticket status'}
            self.write_json()
        else:
            raise HTTPError(400, 'status is not paid on iamport')

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class TicketEnterUserHandler(JsonHandler):
    @user_auth_async
    async def put(self, *args, **kwargs):
        _id = kwargs.get('_id', None)
        if not _id or len(_id) != 24:
            raise HTTPError(400, 'invalid _id')
        ticket = await TicketModel.find_one({'_id': ObjectId(_id)})
        if not ticket:
            raise HTTPError(400, 'not exist ticket')
        if self.current_user['_id'] != ticket['receive_user_oid']:
            raise HTTPError(400, 'not owned by user')
        query = {
            '_id': ObjectId(_id)
        }
        document = {
            '$set': {
                'status': TicketModel.Status.use.name,
                'updated_at': datetime.utcnow()
            }
        }
        self.response['data'] = await TicketModel.update(query, document)
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class TicketRegisterCancelHandler(JsonHandler):
    @user_auth_async
    async def put(self, *args, **kwargs):
        _id = kwargs.get('_id', None)
        if not _id or len(_id) != 24:
            raise HTTPError(400, 'invalid _id')
        ticket = await TicketModel.find_one({'_id': ObjectId(_id)})
        if not ticket:
            raise HTTPError(400, 'not exist ticket')
        if self.current_user['_id'] != ticket['receive_user_oid']:
            raise HTTPError(400, 'not owned by user')
        if ticket['status'] != TicketModel.Status.register.name:
            raise HTTPError(400, 'only register ticket can cancel')
        query = {
            '_id': ObjectId(_id)
        }
        document = {
            '$set': {
                'status': TicketModel.Status.send.name,
                'updated_at': datetime.utcnow()
            }
        }
        result = await TicketModel.update(query, document)
        if result['nModified'] == 1:
            await TicketTypeModel.update({'_id': ticket['ticket_type_oid']}, {'$inc': {'fpfg.now': -1}})
        self.response['data'] = result
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class TicketTypeListMeHandler(JsonHandler):
    @user_auth_async
    @parse_argument([('content_oid', str, None)])
    async def get(self, *args, **kwargs):
        parsed_args = kwargs.get('parsed_args')
        if not parsed_args['content_oid'] or len(parsed_args['content_oid']) != 24:
            raise HTTPError(400, 'invalid content_oid')
        now = datetime.utcnow()
        ticket_types = await TicketTypeModel.find({'content_oid': ObjectId(parsed_args['content_oid']), 'sales_date.end': {'$gte': now}, 'enabled': True}, fields=[('_id')], skip=0, limit=100)
        pipeline = [
            {
                '$match': {
                    'content_oid': ObjectId(parsed_args['content_oid']),
                    'status': TicketModel.Status.send.name,
                    'enabled': True,
                    'receive_user_oid': self.current_user['_id'],
                    'ticket_type_oid': {
                        '$in': [ObjectId(tt['_id']) for tt in ticket_types]
                    }
                }
            },
            {
                '$group': {
                    '_id': '$ticket_type_oid',
                    'ticket_count': {
                        '$sum': 1
                    }
                }
            }
        ]
        aggs = await TicketModel.aggregate(pipeline, 100)
        for a in aggs:
            ticket_type = await TicketTypeModel.get_id(a['_id'], fields=[('name'), ('desc'), ('sales_date'), ('price'), ('color'), ('fpfg'), ('content_oid'), ('show_price')])
            a['name'] = ticket_type['name']
            a['desc'] = ticket_type['desc']
            a['sales_date'] = ticket_type['sales_date']
            a['price'] = ticket_type['price']
            a['color'] = ticket_type['color']
            content = await ContentModel.get_id(ticket_type['content_oid'], fields=[('name')])
            a['content'] = {
                'name': content['name']
            }
            a['fpfg'] = ticket_type['fpfg']
            a['show_price'] = ticket_type['show_price']
        self.response['data'] = aggs
        self.response['count'] = len(aggs)
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class TicketTypeTicketListMeHandler(JsonHandler):
    @user_auth_async
    @parse_argument([('start', int, 0), ('size', int, 10), ('status', str, None)])
    async def get(self, *args, **kwargs):
        _id = kwargs.get('_id', None)
        if not _id or (len(_id) != 24 and len(_id) != 7):
            raise HTTPError(400, 'invalid ticket_type_oid')
        parsed_args = kwargs.get('parsed_args')
        q = {
            '$and': [
                {
                    'ticket_type_oid': ObjectId(_id),
                    'status': parsed_args['status'],
                    'receive_user_oid': self.current_user['_id'],
                    'enabled': True
                }
            ]
        }
        count = await TicketModel.count(query=q)
        result = await TicketModel.find(query=q, fields=[('_id')], skip=parsed_args['start'], limit=parsed_args['size'])
        self.response['data'] = result
        self.response['count'] = count
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class TicketMeCheckRegisterHandler(JsonHandler):
    @user_auth_async
    @parse_argument([('content_oid', str, None)])
    async def get(self, *args, **kwargs):
        parsed_args = kwargs.get('parsed_args')
        if not parsed_args['content_oid'] or len(parsed_args['content_oid']) != 24:
            raise HTTPError(400, 'invalid content_oid')
        q = {
            'content_oid': ObjectId(parsed_args['content_oid']),
            'enabled': True,
            'receive_user_oid': self.current_user['_id'],
            '$or': [
                { 'status': TicketModel.Status.register.name },
                { 'status': TicketModel.Status.pay.name },
                { 'status': TicketModel.Status.use.name }
            ]
        }
        count = await TicketModel.count(query=q)
        if count > 0:
            self.response['data'] = { 'enabled': True }
        else:
            self.response['data'] = { 'enabled': False }
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()
