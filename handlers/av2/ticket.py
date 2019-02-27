# -*- coding: utf-8 -*-

from datetime import datetime
from bson import ObjectId

from tornado.web import HTTPError

from common.decorators import admin_auth_async, parse_argument

from handlers.base import JsonHandler
from models.ticket import TicketTypeModel, TicketModel
from models.content import ContentModel


class TicketTypeHandler(JsonHandler):
    @admin_auth_async
    async def post(self, *args, **kwargs):
        content_oid = self.json_decoded_body.get('content_oid', None)
        if not content_oid or len(content_oid) != 24:
            raise HTTPError(400, self.set_error(1, 'invalid content_oid'))
        content = await ContentModel.get_id(ObjectId(content_oid))
        if not content:
            raise HTTPError(400, self.set_error(2, 'not exist content'))
        ticket_types_count = await TicketTypeModel.count({'content_oid': content['_id'], 'enabled': True})
        if ticket_types_count > TicketTypeModel.MAX:
            raise HTTPError(400, self.set_error(3, 'exceed max ticket type count'))
        ticket_types = self.json_decoded_body.get('ticket_types', None)
        if not ticket_types:
            raise HTTPError(400, self.set_error(1, 'invalid ticket_types'))
        res = list()
        for tt in ticket_types:
            ticket_type = self.validate_ticket_type(tt)
            doc = dict(
                type='network',
                content_oid=content['_id'],
                admin_oid=self.current_user['_id'],
                name=ticket_type['name'],
                desc=dict(
                    value=ticket_type['desc'],
                    enabled=True
                ),
                sales_date=ticket_type['sales_date'],
                price=ticket_type['price'],
                color=ticket_type['color'],
                fpfg=ticket_type['fpfg']
            )
            ttm = TicketTypeModel(raw_data=doc)
            res.append(await ttm.insert())
        self.response['data'] = res
        self.write_json()

    def validate_ticket_type(self, ticket_type):
        if 'name' not in ticket_type:
            raise HTTPError(400, self.set_error(1, 'invalid name'))
        if 'desc' not in ticket_type:
            raise HTTPError(400, self.set_error(1, 'invalid desc'))
        if 'sales_date' not in ticket_type or not isinstance(ticket_type['sales_date'], dict):
            raise HTTPError(400, self.set_error(1, 'invalid sales_date(object)'))
        try:
            ticket_type['sales_date']['start'] = datetime.strptime(ticket_type['sales_date']['start'], '%Y-%m-%dT%H:%M:%S')
            ticket_type['sales_date']['end'] = datetime.strptime(ticket_type['sales_date']['end'], '%Y-%m-%dT%H:%M:%S')
        except ValueError:
            raise HTTPError(400, self.set_error(1, 'invalid sales_date(start/end) format(YYYY-mm-ddTHH:MM:SS)'))
        if 'price' not in ticket_type or not isinstance(ticket_type['price'], int):
            raise HTTPError(400, self.set_error(1, 'invalid price'))
        if 'color' not in ticket_type or ticket_type['color'] not in TicketTypeModel.COLORS:
            raise HTTPError(400, self.set_error(1, 'invalid color (tkit-mint, tkit-coral, hangang-blue, ultra-bora, mustard-norang)'))
        if 'fpfg' not in ticket_type or not isinstance(ticket_type['fpfg'], dict):
            raise HTTPError(400, self.set_error(1, 'invalid fpfg(object)'))
        if 'limit' not in ticket_type['fpfg'] or 'spread' not in ticket_type['fpfg']:
            raise HTTPError(400, self.set_error(1, 'invalid fpfg.limit or fpfg.spread'))
        if ticket_type['fpfg']['limit'] == 0:
            raise HTTPError(400, self.set_error(1, 'invalid fpfg.limit'))
        if ticket_type['fpfg']['spread']:
            if ticket_type['fpfg']['spread'] <= ticket_type['fpfg']['limit']:
                raise HTTPError(400, self.set_error(1, 'invalid fpfg (spread more than limit)'))
        return ticket_type

    @admin_auth_async
    async def get(self, *args, **kwargs):
        _id = kwargs.get('_id', None)
        if not _id or len(_id) != 24:
            raise HTTPError(400, self.set_error(1, 'invalid id'))
        ticket_type = await TicketTypeModel.get_id(ObjectId(_id), fields=[('name'), ('desc'), ('sales_date'), ('price'), ('fpfg')])
        if not ticket_type:
            raise HTTPError(400, self.set_error(2, 'not exist ticket type'))
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
        ticket_type['sales'] = {
            'count': sales_count,
            'limit': ticket_type['fpfg']['limit']
        }
        self.response['data'] = ticket_type
        self.write_json()

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()
