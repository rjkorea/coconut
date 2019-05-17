# -*- coding: utf-8 -*-

from bson import ObjectId
from datetime import datetime

from tornado.web import HTTPError

from common.decorators import user_auth_async, parse_argument

from handlers.base import JsonHandler
from models.content import ContentModel
from models.ticket import TicketTypeModel, TicketModel, TicketLogModel
from models.payment import PaymentModel

from services.iamport import IamportService

import settings


class PaymentHandler(JsonHandler):
    @user_auth_async
    async def post(self, *args, **kwargs):
        content_oid = self.json_decoded_body.get('content_oid', None)
        if not content_oid or len(content_oid) != 24:
            raise HTTPError(400, self.set_error(1, 'invalid content_oid'))
        content = await ContentModel.find_one({'_id': ObjectId(content_oid), 'enabled': True}, fields=[('_id')])
        if not content:
            raise HTTPError(400, self.set_error(2, 'no exist content'))
        ticket_oids = self.json_decoded_body.get('ticket_oids', None)
        if not ticket_oids or not isinstance(ticket_oids, list):
            raise HTTPError(400, self.set_error(3, 'invalid ticket_oids'))
        for t_oid in ticket_oids:
            ticket = await TicketModel.find_one({'_id': ObjectId(t_oid)})
            if not ticket:
                raise HTTPError(400, self.set_error(4, 'no exist ticket'))
            if ticket['receive_user_oid'] != self.current_user['_id'] or ticket['price'] <= 0 or ticket['status'] == TicketModel.Status.pay.name:
                raise HTTPError(400, self.set_error(5, 'invalid ticket'))
        currency = self.json_decoded_body.get('currency', 'KRW')
        if currency not in PaymentModel.CURRENCY:
            raise HTTPError(400, self.set_error(6, 'invalid currency (KRW or USD)'))
        amount = self.json_decoded_body.get('amount', 0)
        if amount <= 0:
            raise HTTPError(400, self.set_error(7, 'invalid amount'))
        payment = PaymentModel(raw_data=dict(
            status='ready',
            user_oid=self.current_user['_id'],
            content_oid=content['_id'],
            currency=currency,
            amount=amount,
            ticket_oids=[ObjectId(t_oid) for t_oid in ticket_oids]
        ))
        _id = await payment.insert()
        config = settings.settings()
        merchant_uid = '%s_%s' % (config['application']['env'], str(_id))
        await PaymentModel.update({'_id': _id, 'enabled': True}, {'$set': {'merchant_uid': merchant_uid}}, False, False)
        self.response['data'] = {
            'merchant_uid': merchant_uid
        }
        self.write_json()

    @user_auth_async
    async def get(self, *args, **kwargs):
        _id = kwargs.get('_id', None)
        if not _id or len(_id) != 24:
            raise HTTPError(400, self.set_error(1, 'invalid _id'))
        q = {
            '_id': ObjectId(_id),
            'user_oid': self.current_user['_id'],
            'enabled': True
        }
        payment = await PaymentModel.find_one(query=q)
        if not payment:
            raise HTTPError(400, self.set_error(2, 'no exist payment'))
        payment['tickets'] = list()
        for oid in payment['ticket_oids']:
            tm = await TicketModel.get_id(oid, fields={'_id': True, 'ticket_type_oid': True})
            ttm = await TicketTypeModel.get_id(tm['ticket_type_oid'], fields={'_id': False, 'name': True, 'desc': True, 'price': True})
            ttm['_id'] = oid
            payment['tickets'].append(ttm)
        payment.pop('ticket_oids')
        self.response['data'] = payment
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class PaymentListHandler(JsonHandler):
    @user_auth_async
    @parse_argument([('start', int, 0), ('size', int, 10), ('content_oid', str, None), ('status', str, None)])
    async def get(self, *args, **kwargs):
        parsed_args = kwargs.get('parsed_args')
        q = {
            'user_oid': self.current_user['_id']
        }
        if parsed_args['content_oid']:
            q['content_oid'] = ObjectId(parsed_args['content_oid'])
        if parsed_args['status']:
            q['status'] = parsed_args['status']
        count = await PaymentModel.count(query=q)
        result = await PaymentModel.find(query=q, skip=parsed_args['start'], limit=parsed_args['size'])
        for res in result:
            res['tickets'] = list()
            for oid in res['ticket_oids']:
                tm = await TicketModel.get_id(oid, fields={'_id': True, 'ticket_type_oid': True})
                ttm = await TicketTypeModel.get_id(tm['ticket_type_oid'], fields={'_id': False, 'name': True, 'desc': True, 'price': True})
                ttm['_id'] = oid
                res['tickets'].append(ttm)
            res.pop('ticket_oids')
        self.response['data'] = result
        self.response['count'] = count
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class PaymentSuccessHandler(JsonHandler):
    @user_auth_async
    async def put(self, *args, **kwargs):
        imp_uid = self.json_decoded_body.get('imp_uid', None)
        if not imp_uid:
            raise HTTPError(400, self.set_error(1, 'invalid imp_uid'))
        merchant_uid = self.json_decoded_body.get('merchant_uid', None)
        if not merchant_uid:
            raise HTTPError(400, self.set_error(2, 'invalid merchant_uid'))
        payment_result = IamportService().client.find(imp_uid=imp_uid)
        payment = await PaymentModel.find_one({'merchant_uid': ObjectId(payment_result['merchant_uid'])})
        if not payment:
            raise HTTPError(400, self.set_error(3, 'invalid payment'))
        if payment['amount'] > 0:
            res = IamportService().client.is_paid(payment['amount'], merchant_uid=payment_result['merchant_uid'])
            if not res:
                raise HTTPError(400, self.set_error(4, 'invalid amount'))
        else:
            raise HTTPError(400, self.set_error(5, 'no exist amount'))
        now = datetime.utcnow()
        set_doc = {
            '$set': {
                'status': 'paid',
                'imp_uid': imp_uid,
                'info': payment_result,
                'updated_at': now
            }
        }
        await PaymentModel.update({'merchant_uid': payment['merchant_uid'], 'enabled': True}, set_doc, False, False)
        result = await TicketModel.update({'_id': {'$in': payment['ticket_oids']}}, {'status': TicketModel.Status.pay.name, 'updated_at': now}, False, True)
        # TODO: check fpfg.now
        self.response['data'] = {
            'payment_oid': str(payment['_id'])
        }
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class PaymentFailHandler(JsonHandler):
    @user_auth_async
    async def put(self, *args, **kwargs):
        imp_uid = self.json_decoded_body.get('imp_uid', None)
        if not imp_uid:
            raise HTTPError(400, self.set_error(1, 'invalid imp_uid'))
        merchant_uid = self.json_decoded_body.get('merchant_uid', None)
        if not merchant_uid:
            raise HTTPError(400, self.set_error(2, 'invalid merchant_uid'))
        error_msg = self.json_decoded_body.get('error_msg', None)
        if not error_msg:
            raise HTTPError(400, self.set_error(4, 'invalid error_msg'))
        payment = await PaymentModel.find_one({'merchant_uid': merchant_uid})
        if not payment:
            raise HTTPError(400, self.set_error(3, 'invalid payment'))
        set_doc = {
            '$set': {
                'status': 'failed',
                'imp_uid': imp_uid,
                'error_msg': error_msg,
                'updated_at': datetime.utcnow()
            }
        }
        await PaymentModel.update({'merchant_uid': merchant_uid}, set_doc, False, False)
        self.response['data'] = {
            'payment_oid': str(payment['_id'])
        }
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class PaymentCancelHandler(JsonHandler):
    async def put(self, *args, **kwargs):
        payment_oid = self.json_decoded_body.get('payment_oid', None)
        if not payment_oid or len(payment_oid) != 24:
            raise HTTPError(400, self.set_error(2, 'invalid payment_oid'))
        payment = await PaymentModel.get_id(ObjectId(payment_oid))
        if not payment:
            raise HTTPError(400, self.set_error(3, 'no exist payment'))
        if payment['status'] != 'paid':
            raise HTTPError(400, self.set_error(4, 'status is not paid'))
        reason = '결제자에 의한 취소'
        try:
            response = IamportService().client.cancel(reason, merchant_uid=payment['merchant_uid'])
        except IamportService().client.ResponseError as e:
            raise HTTPError(400, self.set_error(e.code, e.message))
        now = datetime.utcnow()
        if response['status'] == 'cancelled':
            query = {
                '_id': payment['_id'],
                'status': 'paid'
            }
            set_doc = {
                '$set': {
                    'status': 'cancelled',
                    'info': response,
                    'updated_at': now
                }
            }
            result = await PaymentModel.update(query, set_doc, False, False)
            if result['nModified'] == 1:
                for oid in payment['ticket_oids']:
                    ticket = await TicketModel.get_id(oid)
                    ticket_log_doc = {
                        'action': 'payment_cancel',
                        'content_oid': ticket['content_oid'],
                        'ticket_oid': ticket['_id'],
                        'ticket_type_oid': ticket['ticket_type_oid'],
                        'user_oid': ticket['receive_user_oid']
                    }
                    ticket_log = TicketLogModel(raw_data=ticket_log_doc)
                    await ticket_log.insert()
                query = {
                    '$in': payment['ticket_oids']
                }
                set_doc = {
                    '$set': {
                        'status': TicketModel.Status.send.name,
                        'receive_user_oid': payment['user_oid'],
                        'updated_at': now
                    }
                }
                await TicketModel.update(query, set_doc, False, True)
                self.response['data'] = {
                    'payment_oid': str(payment['_id'])
                }
                self.write_json()
            else:
                HTTPError(400, self.set_error(5, 'invalid payment'))
        else:
            raise HTTPError(400, self.set_error(6, 'invalid status on Iamport'))

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()
