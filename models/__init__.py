# -*- coding: utf-8 -*-

import logging
from bson import ObjectId

from models.user import UserModel
from models.ticket import TicketTypeModel, TicketModel

from services.sms import NexmoService


async def create_ticket(ticket_order):
    ticket_type = await TicketTypeModel.find_one({'_id': ticket_order['ticket_type_oid']})
    for c in range(ticket_order['qty']):
        days = list()
        for i in range(ticket_type['day']):
            if 'fee' in ticket_order:
                days.append(dict(
                    day=i+1,
                    entered=False,
                    fee=ticket_order['fee']
                ))
            else:
                days.append(dict(
                    day=i+1,
                    entered=False
                ))
        ticket = TicketModel(raw_data=dict(
            ticket_order_oid=ticket_order['_id'],
            ticket_type_oid=ticket_type['_id'],
            content_oid=ticket_type['content_oid'],
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

async def create_user(user):
    res = await UserModel.find_one({'mobile_number': user['mobile_number']})
    if res:
        return res 
    else:
        res = UserModel(raw_data=user)
        await res.insert()
        return res.data

async def send_sms(data=dict()):
    response = NexmoService().client.send_message(data)
    logging.info(response)
    if response['messages'][0]['status'] == '0':
        return True
    else:
        return False
