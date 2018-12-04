# -*- coding: utf-8 -*-

from datetime import datetime
from bson import ObjectId

from tornado.web import HTTPError

from common.decorators import admin_auth_async, parse_argument

from handlers.base import JsonHandler, BaseHandler, MultipartFormdataHandler
from models.content import ContentModel
from models.admin import AdminModel
from models.company import CompanyModel
from models.ticket import TicketModel
from models.content_active_user import ContentActiveUser

from services.s3 import S3Service

from common import hashers
import settings


def get_query_by_user(user=None):
    q = {'$and': []}
    if user['role'] == 'super':
        q['$and'].append({})
    elif user['role'] == 'admin':
        q['$and'].append({})
    elif user['role'] == 'host':
        q['$and'].append(
            {
                'company_oid': user['company_oid']
            }
        )
    elif user['role'] == 'staff':
        q['$and'].append(
            {
                'company_oid': user['company_oid']
            }
        )
    elif user['role'] == 'pro':
        q['$and'].append(
            {
                'company_oid': user['company_oid']
            }
        )
    else:
        pass
    return q


class ContentListHandler(JsonHandler):
    @admin_auth_async
    @parse_argument([('start', int, 0), ('size', int, 10), ('q', str, None)])
    async def get(self, *args, **kwargs):
        parsed_args = kwargs.get('parsed_args')
        q = get_query_by_user(self.current_user)
        if not q['$and']:
            raise HTTPError(400, 'invalid role')
        if 'q' in parsed_args and parsed_args['q']:
            search_q = {'$or': [
                {'name': {'$regex': parsed_args['q']}},
                {'desc': {'$regex': parsed_args['q']}},
                {'place': {'$regex': parsed_args['q']}},
                {'genre': {'$regex': parsed_args['q']}},
                {'lineup': {'$regex': parsed_args['q']}}
            ]}
            q['$and'].append(search_q)
        count = await ContentModel.count(query=q)
        result = await ContentModel.find(query=q, skip=parsed_args['start'], limit=parsed_args['size'])
        for res in result:
            res['admin'] = await AdminModel.get_id(res['admin_oid'])
            res.pop('admin_oid')
            res['company'] = await CompanyModel.get_id(res['company_oid'])
            res.pop('company_oid')
        self.response['data'] = result
        self.response['count'] = count
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class ContentHandler(JsonHandler):
    @admin_auth_async
    async def post(self, *args, **kwargs):
        # basic field
        admin_oid = self.current_user['_id']
        name = self.json_decoded_body.get('name', None)
        if not name or len(name) == 0:
            raise HTTPError(400, 'invalid name')
        place = self.json_decoded_body.get('place', None)
        if not place or len(place) == 0:
            raise HTTPError(400, 'invalid place')
        desc = self.json_decoded_body.get('desc', None)

        # generate short id
        while True:
            short_id = hashers.generate_random_string(ContentModel.SHORT_ID_LENGTH)
            duplicated_content = await ContentModel.find({'short_id': short_id})
            if not duplicated_content:
                break

        # create content model
        content = ContentModel(raw_data=dict(
            short_id=short_id,
            admin_oid=admin_oid,
            name=name,
            place=place,
            desc=desc
        ))
        if self.current_user['role'] == 'host' or self.current_user['role'] == 'pro':
            content.data['company_oid'] = self.current_user['company_oid']
        elif self.current_user['role'] == 'super' or self.current_user['role'] == 'admin':
            company_oid = self.json_decoded_body.get('company_oid', None)
            if not company_oid:
                raise HTTPError(400, 'need company_oid when your role is super or admin')
            content.data['company_oid'] = ObjectId(company_oid)
        else:
            pass
        id = await content.insert()
        self.response['data'] = {
            'content_oid': str(id)
        }
        self.write_json()

    @admin_auth_async
    async def put(self, *args, **kwargs):
        _id = kwargs.get('_id', None)
        if not _id or len(_id) != 24:
            raise HTTPError(400, 'invalid _id')
        content = await ContentModel.find_one({'_id': ObjectId(_id)})
        if not content:
            raise HTTPError(400, 'not exist _id')
        query = {
            '_id': ObjectId(_id)
        }
        self.json_decoded_body['updated_at'] = datetime.utcnow()
        document = {
            '$set': self.json_decoded_body
        }
        self.response['data'] = await ContentModel.update(query, document)
        self.write_json()

    @admin_auth_async
    async def get(self, *args, **kwargs):
        _id = kwargs.get('_id', None)
        if not _id or len(_id) != 24:
            raise HTTPError(400, 'invalid _id')
        content = await ContentModel.find_one({'_id': ObjectId(_id)})
        if not content:
            raise HTTPError(400, 'not exist content')
        company = await CompanyModel.get_id(content['company_oid'], fields=[('name')])
        content['company'] = company
        admin = await AdminModel.get_id(content['admin_oid'], fields=[('name')])
        content['admin'] = admin
        self.response['data'] = content
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class ContentPostHandler(JsonHandler):
    @admin_auth_async
    async def post(self, *args, **kwargs):
        admin_oid = self.current_user['_id']
        name = self.json_decoded_body.get('name', None)
        if not name or len(name) == 0:
            raise HTTPError(400, 'invalid name')
        place = self.json_decoded_body.get('place', None)
        if not place or len(place) == 0:
            raise HTTPError(400, 'invalid place')
        when = self.json_decoded_body.get('when', None)
        if not when or not isinstance(when, dict):
            raise HTTPError(400, 'invalid when')
        tags = self.json_decoded_body.get('tags', None)
        if not tags or not isinstance(tags, list):
            raise HTTPError(400, 'invalid tags')
        desc = self.json_decoded_body.get('desc', None)
        notice = self.json_decoded_body.get('notice', {'enabled': False, 'message': '공지사항입니다.'})
        config = settings.settings()
        # generate short id
        while True:
            short_id = hashers.generate_random_string(ContentModel.SHORT_ID_LENGTH)
            duplicated_content = await ContentModel.find({'short_id': short_id})
            if not duplicated_content:
                break
        try:
            if 'start' in when:
                when['start'] = datetime.strptime(when['start'], '%Y-%m-%dT%H:%M:%S')
            if 'end' in when:
                when['end'] = datetime.strptime(when['end'], '%Y-%m-%dT%H:%M:%S')
        except ValueError as e:
            raise HTTPError(400, e)
        # create content model
        doc = {
            'short_id': short_id,
            'admin_oid': admin_oid,
            'name': name,
            'place': place,
            'desc': desc,
            'when': when,
            'tags': tags,
            'sms': {
                'message': 'http://%s:%d/l/%s 기본티켓링크' % (config['web']['host'], config['web']['port'], short_id)
            },
            'image': {
                'poster': {
                    'm': 'https://s3.ap-northeast-2.amazonaws.com/%s/content/default/poster.m.png' % config['aws']['res_bucket']
                },
                'logo': {
                    'm': 'https://s3.ap-northeast-2.amazonaws.com/%s/content/default/logo.m.png' % config['aws']['res_bucket']
                },
                'og': {
                    'm': 'https://s3.ap-northeast-2.amazonaws.com/%s/content/default/og.m.png' % config['aws']['res_bucket']
                },
                'extra': [
                    {
                        'm': 'https://s3.ap-northeast-2.amazonaws.com/%s/content/default/extra_0.m.png' % config['aws']['res_bucket']
                    },
                    {
                        'm': 'https://s3.ap-northeast-2.amazonaws.com/%s/content/default/extra_1.m.png' % config['aws']['res_bucket']
                    },
                    {
                        'm': 'https://s3.ap-northeast-2.amazonaws.com/%s/content/default/extra_2.m.png' % config['aws']['res_bucket']
                    },
                    {
                        'm': 'https://s3.ap-northeast-2.amazonaws.com/%s/content/default/extra_3.m.png' % config['aws']['res_bucket']
                    },
                    {
                        'm': 'https://s3.ap-northeast-2.amazonaws.com/%s/content/default/extra_4.m.png' % config['aws']['res_bucket']
                    }
                ]
            },
            'notice': notice
        }
        content = ContentModel(raw_data=doc)
        if self.current_user['role'] == 'host' or self.current_user['role'] == 'pro':
            content.data['company_oid'] = self.current_user['company_oid']
        elif self.current_user['role'] == 'super' or self.current_user['role'] == 'admin':
            company_oid = self.json_decoded_body.get('company_oid', None)
            if not company_oid:
                raise HTTPError(400, 'need company_oid when your role is super or admin')
            content.data['company_oid'] = ObjectId(company_oid)
        else:
            pass
        content_oid = await content.insert()
        self.response['data'] = {
            'content_oid': content_oid
        }
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class ContentImageUploadHandler(MultipartFormdataHandler):
    @admin_auth_async
    async def post(self, *args, **kwargs):
        content_oid = kwargs.get('_id', None)
        if not content_oid or len(content_oid) != 24:
            raise HTTPError(400, 'invalid content_oid')
        type = kwargs.get('type', None)
        if type not in ContentModel.IMAGE_TYPE:
            raise HTTPError(400, 'invalid type')
        if 'image' not in self.request.files:
            raise HTTPError(400, 'invalid param, only image')
        config = settings.settings()
        img_extension = self.request.files['image'][0]['filename'].split('.')[-1]
        key = 'content/%s/%s.m.%s' % (content_oid, type, img_extension)
        cres = S3Service().client.create_multipart_upload(
            ACL='public-read',
            ContentType='image/%s' % img_extension,
            Bucket=config['aws']['res_bucket'],
            Key=key
        )
        upres = S3Service().client.upload_part(
            UploadId=cres['UploadId'],
            PartNumber=1,
            Body=self.request.files['image'][0]['body'],
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
        query = {
            '_id': ObjectId(content_oid)
        }
        if type == ContentModel.IMAGE_TYPE[0] or type == ContentModel.IMAGE_TYPE[1] or type == ContentModel.IMAGE_TYPE[2]:
            document = {
                '$set': {
                    'image.%s.m' % type: 'https://s3.ap-northeast-2.amazonaws.com/%s/%s?versionId=%s' % (config['aws']['res_bucket'], key, response['VersionId']),
                    'updated_at': datetime.utcnow()
                }
            }
        else:
            document = {
                '$set': {
                    'image.extra.%s.m' % type[-1:]: 'https://s3.ap-northeast-2.amazonaws.com/%s/%s?versionId=%s' % (config['aws']['res_bucket'], key, response['VersionId']),
                    'updated_at': datetime.utcnow()
                }
            }
        await ContentModel.update(query, document, False, False)
        self.response['data'] = document['$set']
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class ContentActiveUserHandler(JsonHandler):
    @admin_auth_async
    async def put(self, *args, **kwargs):
        _id = kwargs.get('_id', None)
        if not _id or len(_id) != 24:
            raise HTTPError(400, 'invalid _id')
        content = await ContentModel.find_one({'_id': ObjectId(_id)})
        if not content:
            raise HTTPError(400, 'not exist _id')

        q = {'content_oid': ObjectId(_id)}
        res = await ContentActiveUser.find(q)
        if res:
            await ContentActiveUser.delete_many(q)
        pipeline = [
            {
                '$match': {
                    'content_oid': ObjectId(_id)
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
                        'mobile_number': '$receive_user.mobile_number'
                    }
                }
            }
        ]
        aggs = await TicketModel.aggregate(pipeline, -1)
        for au in aggs:
            await ContentActiveUser.insert_many({
                'content_oid': ObjectId(_id),
                'name': au['_id']['name'][0],
                'mobile_number': au['_id']['mobile_number'][0]
            })
        self.response['data'] = 'OK'
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()
