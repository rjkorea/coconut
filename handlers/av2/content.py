# -*- coding: utf-8 -*-

from datetime import datetime
from bson import ObjectId

from tornado.web import HTTPError

from common.decorators import admin_auth_async, parse_argument

from handlers.base import JsonHandler, MultipartFormdataHandler
from models.content import ContentModel
from models.admin import AdminModel
from models.company import CompanyModel
from models.ticket import TicketModel

from services.s3 import S3Service

from common import hashers
import settings


class ContentPostHandler(MultipartFormdataHandler):
    @admin_auth_async
    async def post(self, *args, **kwargs):
        is_private = self.json_decoded_body.get('is_private', False)
        name = self.json_decoded_body.get('name', None)
        if not name or len(name) == 0:
            raise HTTPError(400, 'invalid name')
        tags = self.json_decoded_body.get('tags', None)
        if not tags or len(tags) == 0:
            raise HTTPError(400, 'invalid tags')
        images_0 = self.request.files.get('images_0', None)
        if not images_0:
            raise HTTPError(400, 'invalid images_0')
        place_name = self.json_decoded_body.get('place_name', None)
        if not place_name or len(place_name) == 0:
            raise HTTPError(400, 'invalid place_name')
        place_url = self.json_decoded_body.get('place_url', None)
        if not place_url or len(place_url) == 0:
            raise HTTPError(400, 'invalid place_url')
        place_x = self.json_decoded_body.get('place_x', None)
        if not place_x or len(place_x) == 0:
            raise HTTPError(400, 'invalid place_x')
        place_y = self.json_decoded_body.get('place_y', None)
        if not place_y or len(place_y) == 0:
            raise HTTPError(400, 'invalid place_y')
        when_start = self.json_decoded_body.get('when_start', None)
        if not when_start or len(when_start) == 0:
            raise HTTPError(400, 'invalid when_start')
        when_end = self.json_decoded_body.get('when_end', None)
        if not when_end or len(when_end) == 0:
            raise HTTPError(400, 'invalid when_end')
        try:
            when_start = datetime.strptime(when_start, '%Y-%m-%dT%H:%M:%S')
            when_end = datetime.strptime(when_end, '%Y-%m-%dT%H:%M:%S')
        except ValueError:
            raise HTTPError(400, 'invalid date format(YYYY-mm-ddTHH:MM:SS)')
        host_name = self.json_decoded_body.get('host_name', None)
        if not host_name or len(host_name) == 0:
            raise HTTPError(400, 'invalid host_name')
        host_email = self.json_decoded_body.get('host_email', None)
        if not host_email or len(host_email) == 0:
            raise HTTPError(400, 'invalid host_email')
        host_tel = self.json_decoded_body.get('host_tel', None)
        if not host_tel or len(host_tel) == 0:
            raise HTTPError(400, 'invalid host_tel')
        comments_type = self.json_decoded_body.get('comments_type', 'preview')
        if comments_type not in ('preview', 'guestbook'):
            raise HTTPError(400, 'invalid comments_type (preview, guestbook)')
        while True:
            short_id = hashers.generate_random_string(ContentModel.SHORT_ID_LENGTH)
            duplicated_content = await ContentModel.find({'short_id': short_id})
            if not duplicated_content:
                break
        config = settings.settings()
        doc = dict(
            short_id=short_id,
            is_private=is_private,
            name=name,
            tags=[t.strip() for t in tags.split(',')],
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
                name=host_name,
                email=host_email,
                tel=host_tel
            ),
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
            doc['comments']['is_private'] = self.json_decoded_body.get('comments_private')
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
