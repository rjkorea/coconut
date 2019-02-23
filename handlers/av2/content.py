# -*- coding: utf-8 -*-

from datetime import datetime
from bson import ObjectId

from tornado.web import HTTPError

from common.decorators import admin_auth_async, parse_argument

from handlers.base import JsonHandler, MultipartFormdataHandler
from models.content import ContentModel

from services.s3 import S3Service

from common import hashers
import settings


class ContentPostHandler(MultipartFormdataHandler):
    @admin_auth_async
    async def post(self, *args, **kwargs):
        is_private = self.json_decoded_body.get('is_private', False)
        if is_private == 'true':
            is_private = True
        elif is_private == 'false':
            is_private = False
        name = self.json_decoded_body.get('name', None)
        if not name or len(name) == 0:
            raise HTTPError(400, self.set_error(1, 'invalid name'))
        tags = self.json_decoded_body.get('tags', None)
        if not tags or len(tags) == 0:
            raise HTTPError(400, self.set_error(1, 'invalid tags'))
        images_0 = self.request.files.get('images_0', None)
        if not images_0:
            raise HTTPError(400, self.set_error(1, 'invalid images_0'))
        place_name = self.json_decoded_body.get('place_name', None)
        if not place_name or len(place_name) == 0:
            raise HTTPError(400, self.set_error(1, 'invalid place_name'))
        place_url = self.json_decoded_body.get('place_url', None)
        if not place_url or len(place_url) == 0:
            raise HTTPError(400, self.set_error(1, 'invalid place_url'))
        place_x = self.json_decoded_body.get('place_x', None)
        if not place_x or len(place_x) == 0:
            raise HTTPError(400, self.set_error(1, 'invalid place_x'))
        place_y = self.json_decoded_body.get('place_y', None)
        if not place_y or len(place_y) == 0:
            raise HTTPError(400, self.set_error(1, 'invalid place_y'))
        when_start = self.json_decoded_body.get('when_start', None)
        if not when_start or len(when_start) == 0:
            raise HTTPError(400, self.set_error(1, 'invalid when_start'))
        when_end = self.json_decoded_body.get('when_end', None)
        if not when_end or len(when_end) == 0:
            raise HTTPError(400, self.set_error(1, 'invalid when_end'))
        try:
            when_start = datetime.strptime(when_start, '%Y-%m-%dT%H:%M:%S')
            when_end = datetime.strptime(when_end, '%Y-%m-%dT%H:%M:%S')
        except ValueError:
            raise HTTPError(400, self.set_error(1, 'invalid date(when_start/when_end) format(YYYY-mm-ddTHH:MM:SS)'))
        comments_type = self.json_decoded_body.get('comments_type', 'preview')
        if comments_type not in ('preview', 'guestbook'):
            raise HTTPError(400, self.set_error(1, 'invalid comments_type (preview, guestbook)'))
        while True:
            short_id = hashers.generate_random_string(ContentModel.SHORT_ID_LENGTH)
            duplicated_content = await ContentModel.find({'short_id': short_id})
            if not duplicated_content:
                break
        if 'type' in self.current_user and self.current_user['type'] == 'business':
            default_host = dict(
                name=self.current_user['name'],
                email=self.current_user['email'],
                tel=self.current_user['tel']
            )
        else:
            default_host = dict(
                name=self.current_user['name'],
                email=self.current_user['email'],
                tel=self.current_user['mobile_number']
            )
        config = settings.settings()
        doc = dict(
            short_id=short_id,
            is_private=is_private,
            name=name,
            tags=eval(tags),
            place=dict(
                name=place_name,
                url=place_url,
                x=place_x,
                y=place_y
            ),
            when=dict(
                start=when_start,
                end=when_end
            ),
            host=default_host,
            notice=dict(
                enabled=False,
                message=''
            ),
            comments=dict(
                type=comments_type,
                is_private=False
            ),
            admin_oid=self.current_user['_id'],
            company_oid=self.current_user['company_oid'],
            sms=dict(
                message='http://%s:%d/in/%s 기본티켓링크' % (config['web']['host'], config['web']['port'], short_id)
            ),
            images=[
                {
                    'm': None
                },
                {
                    'm': None
                },
                {
                    'm': None
                },
                {
                    'm': None
                },
                {
                    'm': None
                },
                {
                    'm': None
                },
                {
                    'm': None
                }
            ]
        )
        if self.json_decoded_body.get('site_url', None):
            doc['site_url'] = self.json_decoded_body.get('site_url')
        if self.json_decoded_body.get('video_url', None):
            doc['video_url'] = self.json_decoded_body.get('video_url')
        if self.json_decoded_body.get('notice', None):
            doc['notice'] = dict(
                message=self.json_decoded_body.get('notice'),
                enabled=True
            )
        if self.json_decoded_body.get('desc', None):
            doc['desc'] = self.json_decoded_body.get('desc')
        if comments_type:
            doc['comments']['type'] = comments_type
        if self.json_decoded_body.get('comments_private', False):
            if self.json_decoded_body.get('comments_private') == 'true':
                doc['comments']['is_private'] = True
            elif self.json_decoded_body.get('comments_private') == 'false':
                doc['comments']['is_private'] = False
        if self.json_decoded_body.get('host_name', None):
            doc['host']['name'] = self.json_decoded_body.get('host_name')
        if self.json_decoded_body.get('host_email', None):
            doc['host']['email'] = self.json_decoded_body.get('host_email')
        if self.json_decoded_body.get('host_tel', None):
            doc['host']['tel'] = self.json_decoded_body.get('host_tel', None)
        content = ContentModel(raw_data=doc)
        content_oid = await content.insert()

        # image upload to S3
        doc = self.upload_s3(content_oid, self.request.files, config)
        query = {
            '_id': ObjectId(content_oid)
        }
        document = {
            '$set': doc
        }
        await ContentModel.update(query, document, False, False)
        self.response['data'] = {
            'content_oid': content_oid
        }
        self.write_json()

    def upload_s3(self, content_oid, files, config):
        doc = dict()
        for k,v in files.items():
            img_extension = v[0]['filename'].split('.')[-1]
            key = 'content/%s/%s.m.%s' % (content_oid, k, img_extension)
            cres = S3Service().client.create_multipart_upload(
                ACL='public-read',
                ContentType='image/%s' % img_extension,
                Bucket=config['aws']['res_bucket'],
                Key=key
            )
            upres = S3Service().client.upload_part(
                UploadId=cres['UploadId'],
                PartNumber=1,
                Body=v[0]['body'],
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
            doc['images.%s.m'%k[-1]] = 'https://s3.ap-northeast-2.amazonaws.com/%s/%s?versionId=%s' % (config['aws']['res_bucket'], key, response['VersionId'])
        return doc

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class ContentListHandler(JsonHandler):
    @admin_auth_async
    @parse_argument([('status', str, None), ('start', int, 0), ('size', int, 10)])
    async def get(self, *args, **kwargs):
        parsed_args = kwargs.get('parsed_args')
        if 'status' in parsed_args and parsed_args['status'] not in ('open', 'closed'):
            raise HTTPError(400, self.set_error(1, 'invalid status (open, closed)'))
        if self.current_user['role'] == 'super' or self.current_user['role'] == 'admin':
            q = dict(
                enabled=True
            )
        else:
            q = dict(
                company_oid=self.current_user['company_oid'],
                enabled=True
            )
        now = datetime.utcnow()
        if parsed_args['status']:
            if parsed_args['status'] == 'open':
                q['when.end'] = {
                    '$gte': now
                }
            elif parsed_args['status'] == 'closed':
                q['when.end'] = {
                    '$lt': now
                }
        count = await ContentModel.count(query=q)
        result = await ContentModel.find(query=q, sort=[('when.start', 1)], skip=parsed_args['start'], limit=parsed_args['size'])
        self.response['data'] = result
        self.response['count'] = count
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class ContentHandler(JsonHandler):
    @admin_auth_async
    async def get(self, *args, **kwargs):
        _id = kwargs.get('_id', None)
        if not _id or len(_id) != 24:
            raise HTTPError(400, self.set_error(1, 'invalid id'))
        content = await ContentModel.find_one({'_id': ObjectId(_id)})
        if not content:
            raise HTTPError(400, self.set_error(1, 'not exist content'))
        self.response['data'] = content
        self.write_json()

    @admin_auth_async
    async def put(self, *args, **kwargs):
        _id = kwargs.get('_id', None)
        if not _id or len(_id) != 24:
            raise HTTPError(400, self.set_error(1, 'invalid id'))
        content = await ContentModel.find_one({'_id': ObjectId(_id)})
        if not content:
            raise HTTPError(400, self.set_error(1, 'not exist content'))
        is_private = self.json_decoded_body.get('is_private', False)
        if is_private == 'true':
            is_private = True
        elif is_private == 'false':
            is_private = False
        name = self.json_decoded_body.get('name', None)
        tags = self.json_decoded_body.get('tags', None)
        if tags:
            tags=eval(tags)
        else:
            tags=None
        place_name = self.json_decoded_body.get('place_name', None)
        place_url = self.json_decoded_body.get('place_url', None)
        place_x = self.json_decoded_body.get('place_x', None)
        place_y = self.json_decoded_body.get('place_y', None)
        when_start = self.json_decoded_body.get('when_start', None)
        when_end = self.json_decoded_body.get('when_end', None)
        try:
            when_start = datetime.strptime(when_start, '%Y-%m-%dT%H:%M:%S')
            when_end = datetime.strptime(when_end, '%Y-%m-%dT%H:%M:%S')
        except ValueError:
            raise HTTPError(400, self.set_error(1, 'invalid date(when_start/when_end) format(YYYY-mm-ddTHH:MM:SS)'))
        comments_type = self.json_decoded_body.get('comments_type', 'preview')
        if comments_type not in ('preview', 'guestbook'):
            raise HTTPError(400, self.set_error(1, 'invalid comments_type (preview, guestbook)'))
        site_url = self.json_decoded_body.get('site_url', None)
        video_url = self.json_decoded_body.get('video_url', None)
        notice_message = self.json_decoded_body.get('notice', None)
        desc = self.json_decoded_body.get('desc', None)
        if self.json_decoded_body.get('comments_private', False):
            if self.json_decoded_body.get('comments_private') == 'true':
                comments_private = True
            elif self.json_decoded_body.get('comments_private') == 'false':
                comments_private = False
        host_name = self.json_decoded_body.get('host_name', None)
        host_email = self.json_decoded_body.get('host_email', None)
        host_tel = self.json_decoded_body.get('host_tel', None)
        set_doc = dict(
            is_private=is_private,
            name=name,
            tags=tags,
            place=dict(
                name=place_name,
                url=place_url,
                x=place_x,
                y=place_y
            ),
            when=dict(
                start=when_start,
                end=when_end
            ),
            host=dict(
                host_name=host_name,
                host_email=host_email,
                host_tel=host_tel
            ),
            site_url=site_url,
            video_url=video_url,
            notice=dict(
                enabled=True,
                message=notice_message
            ),
            comments=dict(
                type=comments_type,
                is_private=comments_private
            ),
            desc=desc,
            updated_at=datetime.utcnow()
        )
        updated = await ContentModel.update({'_id': content['_id']}, {'$set': set_doc}, False, False)
        self.response['data'] = updated
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()
