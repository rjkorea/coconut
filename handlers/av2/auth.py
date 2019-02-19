# -*- coding: utf-8 -*-

import logging
from bson import ObjectId
from datetime import datetime, timedelta

from tornado.web import HTTPError
from handlers.base import JsonHandler
from models.admin import AdminModel
from models.verification import VerificationModel
from services.sms import NexmoService

from common import hashers


class EmailFindVerificationHandler(JsonHandler):
    async def get(self, *args, **kwargs):
        code = kwargs.get('code', None)
        if not code or len(code) != 6:
            raise HTTPError(400, self.set_error(1, 'invalid verification code'))
        query = {
            'code': code,
            'expired_at': {
                '$gte': datetime.utcnow()
            }
        }
        verification = await VerificationModel.find_one(query)
        if not verification:
            raise HTTPError(400, self.set_error(2, 'expired verification code'))
        admin = await AdminModel.find_one({'mobile_number': verification['mobile_number']}, fields={'mobile_number': True, 'email': True, '_id': False})
        if not admin:
            raise HTTPError(400, self.set_error(3, 'invalid host'))
        self.response['data'] = admin
        self.write_json()

    async def put(self, *args, **kwargs):
        name = self.json_decoded_body.get('name', None)
        if not name or len(name) == 0:
            raise HTTPError(400, self.set_error(1, 'invalid name'))
        mobile_number = self.json_decoded_body.get('mobile_number', None)
        if not mobile_number or len(mobile_number) == 0:
            raise HTTPError(400, self.set_error(1, 'invalid mobile_number'))
        query = {
            'name': name,
            'mobile_number': mobile_number,
            'enabled': True
        }
        last_name = self.json_decoded_body.get('last_name', None)
        if last_name:
            query['last_name'] = last_name
        admin = await AdminModel.find_one(query)
        if not admin:
            raise HTTPError(400, self.set_error(2, 'invalid host'))
        verification_code = hashers.generate_random_number(6)
        doc = {
            'mobile_number': admin['mobile_number'],
            'code': verification_code,
            'expired_at': datetime.utcnow() + timedelta(minutes=3)
        }
        verfication = VerificationModel(raw_data=doc)
        _id = await verfication.insert()
        payload = {
            'type': 'unicode',
            'from': 'TKIT',
            'to': admin['mobile_number'],
            'text': '[TKIT] Verification Code[%s]' % verification_code
        }
        res = NexmoService().client.send_message(payload)
        logging.info(res)
        if res['messages'][0]['status'] != '0':
            raise HTTPError(400, self.set_error(2, '%s: %s' % (res['messages'][0]['status'], res['messages'][0]['error-text'])))
        self.response['message'] = 'sent SMS verification code'
        self.write_json()

    async def options(self, *args, **kwargs):
        self.respose['message'] = 'OK'
        self.write_json()


class PasswordResetVerificationHandler(JsonHandler):
    async def get(self, *args, **kwargs):
        code = kwargs.get('code', None)
        if not code or len(code) != 6:
            raise HTTPError(400, self.set_error(1, 'invalid verification code'))
        query = {
            'code': code,
            'expired_at': {
                '$gte': datetime.utcnow()
            }
        }
        verification = await VerificationModel.find_one(query)
        if not verification:
            raise HTTPError(400, self.set_error(2, 'expired verification code'))
        admin = await AdminModel.find_one({'mobile_number': verification['mobile_number']}, fields={'_id': True})
        if not admin:
            raise HTTPError(400, self.set_error(3, 'invalid host'))
        self.response['data'] = {
            'host_oid': admin['_id']
        }
        self.write_json()

    async def put(self, *args, **kwargs):
        email = self.json_decoded_body.get('email', None)
        if not email or len(email) == 0:
            raise HTTPError(400, self.set_error(1, 'invalid email'))
        name = self.json_decoded_body.get('name', None)
        if not name or len(name) == 0:
            raise HTTPError(400, self.set_error(1, 'invalid name'))
        mobile_number = self.json_decoded_body.get('mobile_number', None)
        if not mobile_number or len(mobile_number) == 0:
            raise HTTPError(400, self.set_error(1, 'invalid mobile_number'))
        query = {
            'email': email,
            'name': name,
            'mobile_number': mobile_number,
            'enabled': True
        }
        last_name = self.json_decoded_body.get('last_name', None)
        if last_name:
            query['last_name'] = last_name
        admin = await AdminModel.find_one(query)
        if not admin:
            raise HTTPError(400, self.set_error(2, 'invalid host'))
        verification_code = hashers.generate_random_number(6)
        doc = {
            'mobile_number': admin['mobile_number'],
            'code': verification_code,
            'expired_at': datetime.utcnow() + timedelta(minutes=3)
        }
        verfication = VerificationModel(raw_data=doc)
        _id = await verfication.insert()
        payload = {
            'type': 'unicode',
            'from': 'TKIT',
            'to': admin['mobile_number'],
            'text': '[TKIT] Verification Code[%s]' % verification_code
        }
        res = NexmoService().client.send_message(payload)
        logging.info(res)
        if res['messages'][0]['status'] != '0':
            raise HTTPError(400, self.set_error(2, '%s: %s' % (res['messages'][0]['status'], res['messages'][0]['error-text'])))
        self.response['message'] = 'sent SMS verification code'
        self.write_json()

    async def options(self, *args, **kwargs):
        self.respose['message'] = 'OK'
        self.write_json()


class PasswordResetHandler(JsonHandler):
    async def put(self, *args, **kwargs):
        host_oid = self.json_decoded_body.get('host_oid', None)
        if not host_oid or len(host_oid) != 24:
            raise HTTPError(400, self.set_error(1, 'invalid host_oid'))
        verification_code = self.json_decoded_body.get('verification_code', None)
        if not verification_code or len(verification_code) == 0:
            raise HTTPError(400, self.set_error(1, 'invalid verification_code'))
        reset_password = self.json_decoded_body.get('reset_password', None)
        if not reset_password or not hashers.validate_password(reset_password):
            raise HTTPError(400, self.set_error(1, 'invalid reset_password'))
        query = {
            '_id': ObjectId(host_oid),
           'enabled': True
        }
        admin = await AdminModel.find_one(query)
        if not admin:
            raise HTTPError(400, self.set_error(2, 'invalid host'))
        query = {
            'code': verification_code,
            'mobile_number': admin['mobile_number'],
            'enabled': True
        }
        verification = await VerificationModel.find_one(query)
        if not verification:
            raise HTTPError(400, self.set_error(2, 'invalid verification code'))
        set = {
            '$set': {
                'password': hashers.make_password(reset_password),
                'updated_at': datetime.utcnow()
            }
        }
        res = await AdminModel.update({'_id': admin['_id']}, set, False, False)
        self.response['message'] = 'done reset password'
        self.write_json()

    async def options(self, *args, **kwargs):
        self.respose['message'] = 'OK'
        self.write_json()
