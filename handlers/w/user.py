# -*- coding: utf-8 -*-

from bson import ObjectId
from datetime import datetime

from tornado.web import HTTPError

from common import hashers
from common.decorators import user_auth_async, parse_argument

from handlers.base import JsonHandler, MultipartFormdataHandler
from models.user import UserModel, UserAutologinModel
from models.session import UserSessionModel
from models import send_sms

from services.s3 import S3Service

import settings


class UserHandler(JsonHandler):
    @parse_argument([('name', str, None), ('mobile_number', str, None)])
    async def get(self, *args, **kwargs):
        parsed_args = kwargs.get('parsed_args')
        if not parsed_args['name']:
            raise HTTPError(400, 'invalid name')
        if not parsed_args['mobile_number']:
            raise HTTPError(400, 'invalid mobile_number')
        q = {
            'name': parsed_args['name'],
            'mobile_number': parsed_args['mobile_number']
        }
        user = await UserModel.find_one(query=q)
        if not user:
            raise HTTPError(400, 'not exist user')
        res = {
            '_id': user['_id']
        }
        if 'password' in user:
            res['has_password'] = True
        else:
            res['has_password'] = False
        if 'terms' in user:
            res['terms'] = user['terms']
        self.response['data'] = res
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class UserNewPasswordHandler(JsonHandler):
    async def put(self, *args, **kwargs):
        user_oid = kwargs.get('_id', None)
        if not user_oid:
            raise HTTPError(400, 'invalid user_oid')
        user = await UserModel.find_one({'_id': ObjectId(user_oid)})
        if not user:
            raise HTTPError(400, 'not exist user')
        if 'password' in user:
            raise HTTPError(400, 'exist password')
        password = self.json_decoded_body.get('password', None)
        if not password or len(password) == 0 or not hashers.validate_user_password(password):
            raise HTTPError(400, 'invalid password')
        password2 = self.json_decoded_body.get('password2', None)
        if not password or len(password) == 0 or not hashers.validate_user_password(password):
            raise HTTPError(400, 'invalid password2')
        if password != password2:
            raise HTTPError(400, 'password and password2 not matched')
        await UserModel.update({'_id': user['_id']}, {'$set': {'password': hashers.make_password(password)}})
        terms = self.json_decoded_body.get('terms', None)
        if terms == True or terms == False:
            document = {
                '$set': {
                    'terms': {'privacy': terms, 'policy': terms}
                }
            }
            await UserModel.update({'_id': ObjectId(user_oid)}, document, False, False)
            user['terms'] = document['$set']['terms']
        session = UserSessionModel()
        session.data['user_oid'] = user['_id']
        session_oid = await session.insert()
        user['usk'] = str(session_oid)
        self.response['data'] = user
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class UserAuthPasswordHandler(JsonHandler):
    async def put(self, *args, **kwargs):
        user_oid = kwargs.get('_id', None)
        if not user_oid:
            raise HTTPError(400, 'invalid user_oid')
        user = await UserModel.find_one({'_id': ObjectId(user_oid)})
        if not user:
            raise HTTPError(400, 'not exist user')
        if 'password' not in user:
            raise HTTPError(400, 'does not set password')
        password = self.json_decoded_body.get('password', None)
        if not password or len(password) == 0 or not hashers.validate_user_password(password):
            raise HTTPError(400, 'invalid password')
        if not hashers.check_password(password, user['password']):
            raise HTTPError(400, 'invalid password')
        terms = self.json_decoded_body.get('terms', None)
        if terms == True or terms == False:
            document = {
                '$set': {
                    'terms': {'privacy': terms, 'policy': terms}
                }
            }
            await UserModel.update({'_id': ObjectId(user_oid)}, document, False, False)
            user['terms'] = document['$set']['terms']
        session = UserSessionModel()
        session.data['user_oid'] = user['_id']
        session_oid = await session.insert()
        user['usk'] = str(session_oid)
        self.response['data'] = user
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class UserMeHandler(JsonHandler):
    @user_auth_async
    async def get(self, *args, **kwargs):
        user = await UserModel.find_one({'_id': self.current_user['_id']}, fields=[('name'), ('mobile'), ('birthday'), ('gender')])
        if not user:
            raise HTTPError(400, 'not exist user')
        self.response['data'] = user
        self.write_json()

    @user_auth_async
    async def put(self, *args, **kwargs):
        set_doc = {
            'updated_at': datetime.utcnow()
        }
        name = self.json_decoded_body.get('name', None)
        if name:
            set_doc['name'] = name
        birthday = self.json_decoded_body.get('birthday', None)
        if birthday:
            set_doc['birthday'] = birthday
        gender = self.json_decoded_body.get('gender', None)
        if gender:
            set_doc['gender'] = gender
        query = {
            '_id': self.current_user['_id']
        }
        document = {
            '$set': set_doc
        }
        self.response['data'] = await UserModel.update(query, document)
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class UserMePasswordHandler(JsonHandler):
    @user_auth_async
    async def put(self, *args, **kwargs):
        new_password_1 = self.json_decoded_body.get('new_password_1', None)
        if not new_password_1 or len(new_password_1) == 0 or not hashers.validate_user_password_v2(new_password_1):
            raise HTTPError(400, 'invalid new_password_1')
        new_password_2 = self.json_decoded_body.get('new_password_2', None)
        if not new_password_2 or len(new_password_2) == 0 or not hashers.validate_user_password_v2(new_password_2):
            raise HTTPError(400, 'invalid new_password_2')
        if new_password_1 != new_password_2:
            raise HTTPError(400, 'new password 1 and 2 not matched')
        query = {
            '_id': self.current_user['_id']
        }
        document = {
            '$set': {
                'password': hashers.make_password(new_password_1),
                'updated_at': datetime.utcnow()
            }
        }
        self.response['data'] = await UserModel.update(query, document)
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class UserMeImageUploadHandler(MultipartFormdataHandler):
    @user_auth_async
    async def post(self, *args, **kwargs):
        user_oid = self.current_user['_id']
        if 'profile' not in self.request.files:
            raise HTTPError(400, 'invalid param, only profile')
        # TODO upload s3
        config = settings.settings()
        img_extension = self.request.files['profile'][0]['filename'].split('.')[-1]
        key = 'user/%s/profile.m.%s' % (str(self.current_user['_id']), img_extension)
        cres = S3Service().client.create_multipart_upload(
            ACL='public-read',
            ContentType='image/%s' % img_extension,
            Bucket=config['aws']['res_bucket'],
            Key=key
        )
        upres = S3Service().client.upload_part(
            UploadId=cres['UploadId'],
            PartNumber=1,
            Body=self.request.files['profile'][0]['body'],
            Bucket=config['aws']['res_bucket'],
            Key=key
        )
        response = S3Service().client.complete_multipart_upload(
            Bucket=config['aws']['res_bucket'],
            Key=key,
            UploadId=cres['UploadId'],
            MultipartUpload={
                'Parts': [
                    {
                        'ETag': upres['ETag'],
                        'PartNumber': 1
                    }
                ]
            }
        )
        img_dict = {
            'profile': {
                'm': 'https://s3.ap-northeast-2.amazonaws.com/%s/%s?versionId=%s' % (config['aws']['res_bucket'], key, response['VersionId'])
            }
        }
        query = {
            '_id': self.current_user['_id']
        }
        document = {
            '$set': {
                'image': img_dict
            }
        }
        await UserModel.update(query, document, False, False)
        self.response['data'] = {
            'image': img_dict
        }
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class AutoLoginHandler(JsonHandler):
    async def put(self, *args, **kwargs):
        name = self.json_decoded_body.get('name', None)
        if not name:
            raise HTTPError(400, 'invalid name')
        mobile_number = self.json_decoded_body.get('mobile_number', None)
        if not mobile_number:
            raise HTTPError(400, 'invalid mobile_number')
        content_oid = self.json_decoded_body.get('content_oid', None)
        if not content_oid:
            raise HTTPError(400, 'invalid content_oid')
        user = await UserModel.find_one({'name': name, 'mobile_number': mobile_number})
        if not user:
            raise HTTPError(400, 'not exist user')
        session = UserSessionModel()
        session.data['user_oid'] = user['_id']
        session_oid = await session.insert()
        usk = str(session_oid)
        userautologin = UserAutologinModel()
        userautologin.data['usk'] = session_oid
        userautologin.data['content_oid'] = ObjectId(content_oid)
        userautologin_oid = await userautologin.insert()
        config = settings.settings()
        is_sent_receiver = await send_sms(
            {
                'type': 'unicode',
                'from': 'tkit',
                'to': mobile_number,
                'text': 'http://%s:%s/autologin/%s' % (config['web']['host'], config['web']['port'], userautologin_oid)
            }
        )
        self.response['message'] = 'check your sms'
        self.response['is_sent_receiver'] = is_sent_receiver
        self.write_json()


    async def get(self, *args, **kwargs):
        autologin_oid = kwargs.get('_id', None)
        if not autologin_oid or len(autologin_oid) != 24:
            raise HTTPError(400, 'invalid autologin_oid')
        result = await UserAutologinModel.find_one({'_id': ObjectId(autologin_oid)})
        if not result:
            raise HTTPError(400, 'not exist autologin session')
        self.response['data'] = result
        self.write_json()

    
    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()
