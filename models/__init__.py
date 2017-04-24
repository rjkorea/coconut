# -*- coding: utf-8 -*-

import logging
from bson import ObjectId

from models.content import ContentModel
from models.admin import AdminModel
from models.user import UserModel
from models.ticket import TicketTypeModel, TicketOrderModel, TicketModel

from services.sms import NexmoService


async def get_content(id):
    return await ContentModel.find_one(query={'_id': id})

async def get_admin(id):
    return await AdminModel.find_one(query={'_id': id})

async def get_ticket_type(id):
    return await TicketTypeModel.find_one(query={'_id': id})

async def get_ticket_order(id):
    return await TicketOrderModel.find_one(query={'_id': id})

async def get_user(id):
    return await UserModel.find_one(query={'_id': id})

async def create_ticket(ticket_order):
    ticket_type = await TicketTypeModel.find_one({'_id': ticket_order['ticket_type_oid']})
    for c in range(ticket_order['qty']):
        days = dict()
        for i in range(ticket_type['day']):
            if 'fee' in ticket_order:
                days[str(i+1)] = dict(
                    entered=False,
                    fee=ticket_order['fee']
                )
            else:
                days[str(i+1)] = dict(
                    entered=False
                )
        ticket = TicketModel(raw_data=dict(
            ticket_order_oid=ticket_order['_id'],
            days=days
        ))
        await ticket.insert()

async def create_broker(receiver):
    broker = await UserModel.find_one({'mobile_number': receiver['mobile_number']})
    if broker:
        return False
    else:
        broker = UserModel(raw_data=dict(
            name=receiver['name'],
            mobile_number=receiver['mobile_number'],
            access_code=receiver['access_code'],
            role=['broker']
        ))
        await broker.insert()
        return True

async def send_sms(data=dict()):
    response = NexmoService().client.send_message(data)
    logging.info(response)
    if response['messages'][0]['status'] == '0':
        return True
    else:
        return False
