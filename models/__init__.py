# -*- coding: utf-8 -*-

from bson import ObjectId

from models.content import ContentModel
from models.admin import AdminModel
from models.user import UserModel
from models.ticket import TicketTypeModel


async def get_content(id):
    return await ContentModel.find_one(query={'_id': id})

async def get_admin(id):
    return await AdminModel.find_one(query={'_id': id})

async def get_ticket_type(id):
    return await TicketTypeModel.find_one(query={'_id': id})

async def get_user(id):
    return await UserModel.find_one(query={'_id': id})
