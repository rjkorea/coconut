# -*- coding: utf-8 -*-

import logging
from bson import ObjectId

from common import hashers

from models.user import UserModel
from models.ticket import TicketTypeModel, TicketModel
from models.group import GroupModel, GroupTicketModel

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
            receive_user_oid=ticket_order['user_oid'],
            ticket_order_oid=ticket_order['_id'],
            ticket_type_oid=ticket_type['_id'],
            type=ticket_type['type'],
            content_oid=ticket_type['content_oid'],
            days=days
        ))
        if 'slug' in ticket_order:
            # generate serial_number
            while True:
                serial_number = hashers.generate_random_string(TicketModel.SERIAL_NUMBER_LENGTH)
                duplicated_ticket = await TicketModel.find_one({'serial_number': serial_number})
                if not duplicated_ticket:
                    ticket.data['serial_number'] = serial_number
                    break
        await ticket.insert()

async def create_group_ticket(group):
    for c in range(group['qty']):
        ticket = GroupTicketModel(raw_data=dict(
            content_oid=group['content_oid'],
            group_oid=group['_id']
        ))
        await ticket.insert()

async def create_broker(receiver):
    broker = await UserModel.find_one({'mobile_number': receiver['mobile_number'], 'enabled': True})
    if broker:
        return broker['_id']
    else:
        broker = UserModel(raw_data=dict(
            name=receiver['name'],
            mobile_number=receiver['mobile_number']
        ))
        id = await broker.insert()
        return id

async def create_user(user):
    res = await UserModel.find_one({'mobile_number': user['mobile_number'], 'enabled': True})
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

async def create_user_v2(mobile, name):
    user = await UserModel.find_one({'mobile.country_code': mobile['country_code'], 'mobile.number': mobile['number'], 'enabled': True})
    if user:
        return user['_id']
    else:
        user = UserModel(raw_data=dict(
            name=name,
            mobile=mobile
        ))
        id = await user.insert()
        return id
