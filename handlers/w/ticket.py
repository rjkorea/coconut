# -*- coding: utf-8 -*-

from bson import ObjectId
from datetime import datetime

from tornado.web import HTTPError

from common import hashers
from common.decorators import user_auth_async, parse_argument

from handlers.base import JsonHandler
from models.user import UserModel, UserSendHistoryModel
from models.content import ContentModel
from models.ticket import TicketOrderModel, TicketTypeModel, TicketModel, TicketLogModel

from models import create_user

from services.iamport import IamportService


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
        for t_oid in ticket_oids:
            ticket = await TicketModel.find_one({'_id': ObjectId(t_oid)})
            if ticket and ticket['receive_user_oid'] != self.current_user['_id']:
                raise HTTPError(400, 'is not your ticket')
        receive_user = self.json_decoded_body.get('receive_user', None)
        if not receive_user or not isinstance(receive_user, dict):
            raise HTTPError(400, 'invalid receive_user')
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
                        {'status': TicketModel.Status.register.name}
                    ]
                }
            ]
        }
        if parsed_args['content_oid']:
            q['$and'][0]['content_oid'] = ObjectId(parsed_args['content_oid'])
        count = await TicketModel.count(query=q)
        result = await TicketModel.find(query=q, sort=[('updated_at', -1)], skip=parsed_args['start'], limit=parsed_args['size'])
        for res in result:
            res['ticket_type'] = await TicketTypeModel.get_id(res['ticket_type_oid'], fields={'_id': True, 'name': True, 'desc': True, 'price': True, 'sales_date': True, 'color': True})
            res.pop('ticket_type_oid')
            res['content'] = await ContentModel.get_id(res['content_oid'], fields={'_id': True, 'name': True})
            res.pop('content_oid')
        self.response['data'] = result
        self.response['count'] = count
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class TicketListHandler(JsonHandler):
    @user_auth_async
    @parse_argument([('start', int, 0), ('size', int, 10), ('content_oid', str, None)])
    async def get(self, *args, **kwargs):
        parsed_args = kwargs.get('parsed_args')
        q = {
            'receive_user_oid': self.current_user['_id'],
            'enabled': True,
            '$or': [
                {'status': TicketModel.Status.send.name},
                {'status': TicketModel.Status.pay.name}
            ]
        }
        if parsed_args['content_oid']:
            q['content_oid'] = ObjectId(parsed_args['content_oid'])
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
                user = await UserModel.get_id(user_oid, fields=[('name'), ('mobile')])
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
        count = await TicketModel.count(query=q)
        result = await TicketModel.find(query=q, skip=parsed_args['start'], limit=parsed_args['size'])
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
            if 'history_send_user_oids' in res:
                res['history_send_users'] = list()
                for user_oid in res['history_send_user_oids']:
                    user = await UserModel.get_id(user_oid, fields=[('name'), ('mobile')])
                    res['history_send_users'].append(user)
                res.pop('history_send_user_oids')
        self.response['data'] = result
        self.response['count'] = count
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
        for h in history:
            h['mobile_number'] = "%s%s" % (h['mobile']['country_code'], h['mobile']['number'])
            h.pop('mobile')
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
            'send_user_oid': self.current_user['_id']
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
            for oid in res['ticket_oids']:
                tm = await TicketModel.get_id(oid, fields=[('ticket_type_oid')])
                ttm = await TicketTypeModel.get_id(tm['ticket_type_oid'], fields=[('name'), ('desc')])
                res['tickets'].append(ttm)
            res.pop('ticket_oids')
        self.response['data'] = result
        self.response['count'] = count
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
        # aggregate ticket type
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
        aggs = await TicketModel.aggregate(pipeline, 50)
        for a in aggs:
            ticket_type = await TicketTypeModel.get_id(a['_id'])
            a['name'] = ticket_type['name']
            a['desc'] = ticket_type['desc']
            a['sales_date'] = ticket_type['sales_date']
            a['price'] = ticket_type['price']
            if 'color' in ticket_type:
                a['color'] = ticket_type['color']
            content = await ContentModel.get_id(ticket_type['content_oid'])
            a['content'] = {
                'name': content['name']
            }
            query = {
                '$and': [
                    {'enabled': True},
                    {'ticket_type_oid': ticket_type['_id']},
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
            a['sales'] = {
                'count': sales_count,
                'limit': ticket_type['fpfg']['limit']
            }
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
