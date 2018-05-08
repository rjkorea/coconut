# -*- coding: utf-8 -*-

from datetime import datetime
from bson import ObjectId

from tornado.web import HTTPError

from common.decorators import admin_auth_async, parse_argument

from handlers.base import JsonHandler
from models.group import GroupModel, GroupTicketModel
from models.content import ContentModel

from models import create_group_ticket


class GroupListHandler(JsonHandler):
    @admin_auth_async
    @parse_argument([('start', int, 0), ('size', int, 10), ('q', str, None)])
    async def get(self, *args, **kwargs):
        _id = kwargs.get('_id', None)
        if not _id or len(_id) != 24:
            raise HTTPError(400, 'invalid _id')
        content = await ContentModel.find_one({'_id': ObjectId(_id)})
        if not content:
            raise HTTPError(400, 'no exists content')
        parsed_args = kwargs.get('parsed_args')
        q = dict(
            content_oid=content['_id']
        )
        if 'q' in parsed_args and parsed_args['q']:
            q['$or'] = [
                {'name': {'$regex': parsed_args['q']}},
                {'desc': {'$regex': parsed_args['q']}}
            ]
        count = await GroupModel.count(query=q)
        res = await GroupModel.find(query=q, skip=parsed_args['start'], limit=parsed_args['size'])
        for r in res:
            r['used_gt_cnt'] = await GroupTicketModel.count(query={'content_oid': content['_id'], 'group_oid': r['_id'], 'used': True})
            r['reg_gt_cnt'] = await GroupTicketModel.count(query={'content_oid': content['_id'], 'group_oid': r['_id'], 'mobile_number': {'$exists': True}})
        self.response['data'] = res
        self.response['count'] = count
        group_ticket_count = await GroupTicketModel.count(query={'content_oid': content['_id']})
        self.response['group_ticket_count'] = group_ticket_count
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class GroupHandler(JsonHandler):
    @admin_auth_async
    async def get(self, *args, **kwargs):
        content_oid = kwargs.get('content_oid', None)
        if not content_oid or len(content_oid) != 24:
            raise HTTPError(400, 'invalid content_oid')
        content = await ContentModel.find_one({'_id': ObjectId(content_oid)})
        if not content:
            raise HTTPError(400, 'no exists content')
        group_oid = kwargs.get('group_oid', None)
        if not group_oid or len(group_oid) != 24:
            raise HTTPError(400, 'invalid group_oid')
        group = await GroupModel.find_one({'_id': ObjectId(group_oid), 'content_oid': content['_id']})
        if not group:
            raise HTTPError(400, 'no exists group')
        self.response['data'] = group
        self.write_json()
    
    @admin_auth_async
    async def post(self, *args, **kwargs):
        _id = kwargs.get('_id', None)
        if not _id or len(_id) != 24:
            raise HTTPError(400, 'invalid _id')
        content = await ContentModel.find_one({'_id': ObjectId(_id)})
        if not content:
            raise HTTPError(400, 'no exists content')
        admin_oid = self.current_user['_id']
        name = self.json_decoded_body.get('name', None)
        if not name or len(name) == 0:
            raise HTTPError(400, 'invalid name')
        desc = self.json_decoded_body.get('desc', None)
        if not desc or len(desc) == 0:
            raise HTTPError(400, 'invalid desc')
        qty = self.json_decoded_body.get('qty', 0)
        if not isinstance(qty, int) or qty <= 0:
            raise HTTPError(400, 'invalid qty')
        group = GroupModel(raw_data=dict(
            admin_oid=admin_oid,
            content_oid=content['_id'],
            name=name,
            desc=desc,
            qty=qty
        ))
        group_oid = await group.insert()
        await create_group_ticket(group.data)
        self.response['data'] = {
            '_id': group_oid
        }
        self.write_json()

    @admin_auth_async
    async def put(self, *args, **kwargs):
        content_oid = kwargs.get('content_oid', None)
        if not content_oid or len(content_oid) != 24:
            raise HTTPError(400, 'invalid content_oid')
        content = await ContentModel.find_one({'_id': ObjectId(content_oid)})
        if not content:
            raise HTTPError(400, 'no exists content')
        group_oid = kwargs.get('group_oid', None)
        if not group_oid or len(group_oid) != 24:
            raise HTTPError(400, 'invalid group_oid')
        group = await GroupModel.find_one({'_id': ObjectId(group_oid), 'content_oid': content['_id']})
        if not group:
            raise HTTPError(400, 'no exists group')
        query = {
            '_id': group['_id'],
        }
        self.json_decoded_body['updated_at'] = datetime.utcnow()
        document = {
            '$set': self.json_decoded_body
        }
        self.response['data'] = await GroupModel.update(query, document)
        self.write_json()
        
    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class GroupTicketListHandler(JsonHandler):
    @admin_auth_async
    @parse_argument([('start', int, 0), ('size', int, 10), ('q', str, None)])
    async def get(self, *args, **kwargs):
        content_oid = kwargs.get('content_oid', None)
        if not content_oid or len(content_oid) != 24:
            raise HTTPError(400, 'invalid content_oid')
        content = await ContentModel.find_one({'_id': ObjectId(content_oid)})
        if not content:
            raise HTTPError(400, 'no exists content')
        group_oid = kwargs.get('group_oid', None)
        if not group_oid or len(group_oid) != 24:
            raise HTTPError(400, 'invalid group_oid')
        group = await GroupModel.find_one({'_id': ObjectId(group_oid)})
        if not group:
            raise HTTPError(400, 'no exists group')
        parsed_args = kwargs.get('parsed_args')
        q = dict(
            content_oid=ObjectId(content_oid),
            group_oid=ObjectId(group_oid)
        )
        if 'q' in parsed_args and parsed_args['q']:
            q['$or'] = [
                {'name': {'$regex': parsed_args['q']}},
                {'mobile_number': {'$regex': parsed_args['q']}}
            ]
        count = await GroupTicketModel.count(query=q)
        result = await GroupTicketModel.find(query=q, skip=parsed_args['start'], limit=parsed_args['size'])
        self.response['data'] = result
        self.response['count'] = count
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class GroupTicketHandler(JsonHandler):
    @admin_auth_async
    async def post(self, *args, **kwargs):
        content_oid = kwargs.get('content_oid', None)
        if not content_oid or len(content_oid) != 24:
            raise HTTPError(400, 'invalid content_oid')
        content = await ContentModel.find_one({'_id': ObjectId(content_oid)})
        if not content:
            raise HTTPError(400, 'no exists content')
        group_oid = kwargs.get('group_oid', None)
        if not group_oid or len(group_oid) != 24:
            raise HTTPError(400, 'invalid group_oid')
        group = await GroupModel.find_one({'_id': ObjectId(group_oid), 'content_oid': content['_id']})
        if not group:
            raise HTTPError(400, 'no exists group')
        group_ticket = GroupTicketModel(raw_data=dict(
            content_oid=content['_id'],
            group_oid=group['_id']
        ))
        group_ticket_oid = await group_ticket.insert()
        if group_ticket_oid:
            query = {
                '_id': group['_id']
            }
            document = {
                '$inc': {
                    'qty': 1
                }
            }
            await GroupModel.update(query, document)
        self.response['data'] = {
            '_id': group_ticket_oid
        }
        self.write_json()

    @admin_auth_async
    async def get(self, *args, **kwargs):
        content_oid = kwargs.get('content_oid', None)
        if not content_oid or len(content_oid) != 24:
            raise HTTPError(400, 'invalid content_oid')
        content = await ContentModel.find_one({'_id': ObjectId(content_oid)})
        if not content:
            raise HTTPError(400, 'no exists content')
        group_oid = kwargs.get('group_oid', None)
        if not group_oid or len(group_oid) != 24:
            raise HTTPError(400, 'invalid group_oid')
        group = await GroupModel.find_one({'_id': ObjectId(group_oid), 'content_oid': content['_id']})
        if not group:
            raise HTTPError(400, 'no exists group')
        ticket_oid = kwargs.get('ticket_oid', None)
        if not ticket_oid or len(ticket_oid) != 24:
            raise HTTPError(400, 'invalid ticket_oid')
        ticket = await GroupTicketModel.find_one({'_id': ObjectId(ticket_oid), 'group_oid': group['_id'], 'content_oid': content['_id']})
        if not ticket:
            raise HTTPError(400, 'no exists ticket')
        self.response['data'] = ticket
        self.write_json()

    @admin_auth_async
    async def put(self, *args, **kwargs):
        content_oid = kwargs.get('content_oid', None)
        if not content_oid or len(content_oid) != 24:
            raise HTTPError(400, 'invalid content_oid')
        content = await ContentModel.find_one({'_id': ObjectId(content_oid)})
        if not content:
            raise HTTPError(400, 'no exists content')
        group_oid = kwargs.get('group_oid', None)
        if not group_oid or len(group_oid) != 24:
            raise HTTPError(400, 'invalid group_oid')
        group = await GroupModel.find_one({'_id': ObjectId(group_oid), 'content_oid': content['_id']})
        if not group:
            raise HTTPError(400, 'no exists group')
        ticket_oid = kwargs.get('ticket_oid', None)
        if not ticket_oid or len(ticket_oid) != 24:
            raise HTTPError(400, 'invalid ticket_oid')
        ticket = await GroupTicketModel.find_one({'_id': ObjectId(ticket_oid), 'group_oid': group['_id'], 'content_oid': content['_id']})
        if not ticket:
            raise HTTPError(400, 'no exists ticket')
        duplicated_ticket = await GroupTicketModel.find_one({'content_oid': content['_id'], 'mobile_number': self.json_decoded_body['mobile_number'], '_id': {'$ne': ticket['_id']}})
        if duplicated_ticket:
            raise HTTPError(400, '%s가(이) %s를 사용하고 있습니다.' % (duplicated_ticket['name'], duplicated_ticket['mobile_number']))
        query = {
            '_id': ticket['_id'],
        }
        self.json_decoded_body['updated_at'] = datetime.utcnow()
        document = {
            '$set': self.json_decoded_body
        }
        self.response['data'] = await GroupTicketModel.update(query, document)
        self.write_json()
        
    @admin_auth_async
    async def delete(self, *args, **kwargs):
        content_oid = kwargs.get('content_oid', None)
        if not content_oid or len(content_oid) != 24:
            raise HTTPError(400, 'invalid content_oid')
        content = await ContentModel.find_one({'_id': ObjectId(content_oid)})
        if not content:
            raise HTTPError(400, 'no exists content')
        group_oid = kwargs.get('group_oid', None)
        if not group_oid or len(group_oid) != 24:
            raise HTTPError(400, 'invalid group_oid')
        group = await GroupModel.find_one({'_id': ObjectId(group_oid), 'content_oid': content['_id']})
        if not group:
            raise HTTPError(400, 'no exists group')
        ticket_oid = kwargs.get('ticket_oid', None)
        if not ticket_oid or len(ticket_oid) != 24:
            raise HTTPError(400, 'invalid ticket_oid')
        ticket = await GroupTicketModel.find_one({'_id': ObjectId(ticket_oid), 'group_oid': group['_id'], 'content_oid': content['_id']})
        if not ticket:
            raise HTTPError(400, 'no exists ticket')
        res = await GroupTicketModel.delete_many({'_id': ticket['_id']})
        if res.deleted_count == 1:
            query = {
                '_id': group['_id']
            }
            document = {
                '$inc': {
                    'qty': -1
                }
            }
            await GroupModel.update(query, document)
        self.response['data'] = res.deleted_count
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()


class GroupTicketResetHandler(JsonHandler):
    @admin_auth_async
    async def put(self, *args, **kwargs):
        content_oid = kwargs.get('content_oid', None)
        if not content_oid or len(content_oid) != 24:
            raise HTTPError(400, 'invalid content_oid')
        content = await ContentModel.find_one({'_id': ObjectId(content_oid)})
        if not content:
            raise HTTPError(400, 'no exists content')
        group_oid = kwargs.get('group_oid', None)
        if not group_oid or len(group_oid) != 24:
            raise HTTPError(400, 'invalid group_oid')
        group = await GroupModel.find_one({'_id': ObjectId(group_oid), 'content_oid': content['_id']})
        if not group:
            raise HTTPError(400, 'no exists group')
        ticket_oid = kwargs.get('ticket_oid', None)
        if not ticket_oid or len(ticket_oid) != 24:
            raise HTTPError(400, 'invalid ticket_oid')
        ticket = await GroupTicketModel.find_one({'_id': ObjectId(ticket_oid), 'group_oid': group['_id'], 'content_oid': content['_id']})
        if not ticket:
            raise HTTPError(400, 'no exists ticket')
        query = {
            '_id': ticket['_id'],
        }
        document = {
            '$set': {
                'used': False,
                'updated_at': datetime.utcnow()
            },
            '$unset': {
                'name': 1,
                'mobile_number': 1
            }
        }
        self.response['data'] = await GroupTicketModel.update(query, document)
        self.write_json()
        
    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()