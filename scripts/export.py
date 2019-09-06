# -*- coding: utf-8 -*-

from datetime import datetime
from bson import ObjectId
from pprint import pprint

import csv
import click
from pymongo import MongoClient

from iamport import Iamport


@click.group()
def group_ticket():
    pass

@group_ticket.command()
@click.option('-c', '--csvfile', help='csv filename')
@click.option('-m', '--mongo', default='localhost:27017', help='host of mongodb')
@click.option('-i', '--contentid', help='content id')
@click.option('--dryrun', is_flag=True, help='dry run test')
@click.confirmation_option(help='Are you sure you export to csv file?')
def group_tickets(csvfile, mongo, contentid, dryrun):
    click.secho('= params info =', fg='cyan')
    click.secho('csvfile: %s' % (csvfile), fg='green')
    click.secho('mongodb: %s' % (mongo), fg='green')
    now = datetime.utcnow()
    if csvfile and mongo and contentid:
        fieldnames = ['group_name', 'group_desc', 'name', 'mobile_number', 'used']
        writer = csv.DictWriter(open(csvfile, 'w'), fieldnames=fieldnames)
        writer.writeheader()
        mongo_client = MongoClient(host=mongo.split(':')[0], port=int(mongo.split(':')[1]))
        cursor = mongo_client['coconut']['group_ticket'].find({'content_oid': ObjectId(contentid)})
        while cursor.alive:
            doc = cursor.next()
            group = mongo_client['coconut']['group'].find_one({'_id': doc['group_oid']})
            row = dict(
                group_name=group['name'],
                group_desc=group['desc'],
                name='',
                mobile_number='',
                used=doc['used']
            )
            if 'name' in doc:
                row['name'] = doc['name']
            if 'mobile_number' in doc:
                row['mobile_number'] = doc['mobile_number']
            writer.writerow(row)
    else:
        click.secho('check parameters <python export.py  --help>', fg='red')


@click.group()
def user_ticket():
    pass

@user_ticket.command()
@click.option('-c', '--csvfile', help='csv filename')
@click.option('-m', '--mongo', default='localhost:27017', help='host of mongodb')
@click.option('-i', '--contentid', help='content id')
@click.option('--dryrun', is_flag=True, help='dry run test')
@click.confirmation_option(help='Are you sure you import to mongodb?')
def user_tickets(csvfile, mongo, contentid, dryrun):
    click.secho('= params info =', fg='cyan')
    click.secho('csvfile: %s' % (csvfile), fg='green')
    click.secho('mongodb: %s' % (mongo), fg='green')
    now = datetime.utcnow()
    if csvfile and mongo and contentid:
        fieldnames = ['ticket_name', 'price', 'name', 'mobile_number', 'gender', 'birthday', 'status']
        writer = csv.writer(open(csvfile, 'w'))
        mongo_client = MongoClient(host=mongo.split(':')[0], port=int(mongo.split(':')[1]))
        cursor = mongo_client['coconut']['ticket'].find({'content_oid': ObjectId(contentid)})
        while cursor.alive:
            doc = cursor.next()
            user = mongo_client['coconut']['user'].find_one({'_id': doc['receive_user_oid']})
            ticket = mongo_client['coconut']['ticket_type'].find_one({'_id': doc['ticket_type_oid']})
            if 'last_name' in user:
                name = user['last_name'] + user['name']
            else:
                name = user['name']
            if 'gender' in user:
                gender = user['gender']
            else:
                gender = None
            if 'birthday' in user:
                birthday = user['birthday']
            else:
                birthday = None
            line = [ticket['name'], doc['price'], name, user['mobile']['number'], gender, birthday, doc['status']]
            if dryrun:
                pprint(line)
            else:
                writer.writerow(line)
    else:
        click.secho('check parameters <python export.py  --help>', fg='red')


@click.group()
def report_ticket():
    pass

@report_ticket.command()
@click.option('-c', '--csvfile', help='csv filename')
@click.option('-m', '--mongo', default='localhost:27017', help='host of mongodb')
@click.option('-i', '--contentid', help='content id')
@click.option('--dryrun', is_flag=True, help='dry run test')
@click.confirmation_option(help='Are you sure you export to csv file?')
def report_tickets(csvfile, mongo, contentid, dryrun):
    click.secho('= params info =', fg='cyan')
    click.secho('csvfile: %s' % (csvfile), fg='green')
    click.secho('mongodb: %s' % (mongo), fg='green')
    if csvfile and mongo:
        iamport_client = Iamport(imp_key='4335180923213950', imp_secret='8PJ0Bmp6JLDTBITQ281p2BuM5jJ0FpWOeGOQ2eWMZAGBizrkHtKK4ewaygadG72VORLR5IE5ikHBT8WA')
        fieldnames = ['_id', 'content_name', 'ticket_type_name', 'ticket_type_desc', 'price', 'pay_type', 'pay_method', 'pg_provider', 'card_name', 'paid_at', 'status', 'user_name', 'user_mobile_number']
        writer = csv.DictWriter(open(csvfile, 'w'), fieldnames=fieldnames)
        writer.writeheader()
        mongo_client = MongoClient(host=mongo.split(':')[0], port=int(mongo.split(':')[1]))
        if contentid:
            q = {
                 '$and': [
                     {'content_oid': ObjectId(contentid)},
                     {
                         '$or': [
                             {'status': 'use'},
                             {'status': 'pay'}
                         ]
                     }
                 ]
             }
        else:
            q = {}
        tickets = list()
        cursor = mongo_client['coconut']['ticket'].find(q)
        while cursor.alive:
            doc = cursor.next()
            content = mongo_client['coconut']['content'].find_one({'_id': doc['content_oid']}, {'_id': 0, 'name': 1})
            doc['content'] = content
            ticket_type = mongo_client['coconut']['ticket_type'].find_one({'_id': doc['ticket_type_oid']}, {'_id': 0, 'name': 1, 'desc.value': 1})
            doc['ticket_type'] = ticket_type
            receive_user = mongo_client['coconut']['user'].find_one({'_id': doc['receive_user_oid']}, {'_id': 0, 'name': 1, 'mobile': 1})
            doc['receive_user'] = receive_user
            tickets.append(doc)
        if dryrun:
            pprint(tickets)
            pprint(len(tickets))
        else:
            for ticket in tickets:
                row = dict(
                    _id=str(ticket['_id']),
                    content_name=ticket['content']['name'],
                    ticket_type_name=ticket['ticket_type']['name'],
                    ticket_type_desc=ticket['ticket_type']['desc']['value'],
                    price=ticket['price'],
                    pay_type='',
                    pay_method='',
                    pg_provider='',
                    card_name='',
                    paid_at='',
                    status=ticket['status'],
                    user_name=ticket['receive_user']['name'],
                    user_mobile_number=ticket['receive_user']['mobile']['number']
                )
                pay_online = iamport_client.find(merchant_uid=str(ticket['_id']))
                if pay_online and pay_online['status'] == 'paid':
                    row['pay_type'] = 'online'
                    row['pg_provider']= pay_online['pg_provider']
                    row['card_name'] = pay_online['card_name']
                    row['paid_at'] = datetime.fromtimestamp(pay_online['paid_at'])
                else:
                    row['pay_type'] = 'offline'
                writer.writerow(row)
            pprint(len(tickets))

    else:
        click.secho('check parameters <python export.py  --help>', fg='red')


@click.group()
def use_ticket():
    pass

@use_ticket.command()
@click.option('-c', '--csvfile', help='csv filename')
@click.option('-m', '--mongo', default='localhost:27017', help='host of mongodb')
@click.option('-i', '--contentid', help='content id')
@click.option('--dryrun', is_flag=True, help='dry run test')
@click.confirmation_option(help='Are you sure you export to csv file?')
def use_tickets(csvfile, mongo, contentid, dryrun):
    click.secho('= params info =', fg='cyan')
    click.secho('csvfile: %s' % (csvfile), fg='green')
    click.secho('mongodb: %s' % (mongo), fg='green')
    if csvfile and mongo:
        fieldnames = ['content_name', 'ticket_type_name', 'ticket_type_desc', 'status', 'path', 'user_name', 'user_mobile_country_code', 'user_mobile_number', 'birthday', 'gender']
        writer = csv.DictWriter(open(csvfile, 'w'), fieldnames=fieldnames)
        writer.writeheader()
        mongo_client = MongoClient(host=mongo.split(':')[0], port=int(mongo.split(':')[1]))
        if contentid:
            q = {
                 '$and': [
                     {'content_oid': ObjectId(contentid)},
                     {
                         '$or': [
                             {'status': 'send'},
                             {'status': 'register'},
                             {'status': 'pay'},
                             {'status': 'use'},
                             {'status': 'cancel'}
                         ]
                     }
                 ]
             }
        else:
            q = {}
        tickets = list()
        cursor = mongo_client['coconut']['ticket'].find(q)
        while cursor.alive:
            doc = cursor.next()
            content = mongo_client['coconut']['content'].find_one({'_id': doc['content_oid']}, {'_id': 0, 'name': 1})
            doc['content'] = content
            ticket_type = mongo_client['coconut']['ticket_type'].find_one({'_id': doc['ticket_type_oid']}, {'_id': 0, 'name': 1, 'desc.value': 1})
            doc['ticket_type'] = ticket_type
            receive_user = mongo_client['coconut']['user'].find_one({'_id': doc['receive_user_oid']}, {'_id': 0, 'name': 1, 'last_name': 1, 'mobile': 1, 'birthday': 1, 'gender': 1})
            doc['receive_user'] = receive_user
            tickets.append(doc)
        if dryrun:
            pprint(tickets)
            pprint(len(tickets))
        else:
            for ticket in tickets:
                if not ticket['receive_user']:
                    continue
                if 'last_name' in ticket['receive_user']:
                    name = '%s%s' % (ticket['receive_user']['last_name'], ticket['receive_user']['name'])
                else:
                    name = ticket['receive_user']['name']
                if 'birthday' in ticket['receive_user']:
                    birthday = ticket['receive_user']['birthday'][:4]
                else:
                    birthday = None
                if 'gender' in ticket['receive_user']:
                    gender = ticket['receive_user']['gender']
                else:
                    gender = None
                if 'history_send_user_oids' in ticket:
                    path = list()
                    for u in ticket['history_send_user_oids']:
                        path_user = mongo_client['coconut']['user'].find_one({'_id': u}, {'_id': 0, 'name': 1, 'last_name': 1, 'mobile': 1})
                        if 'last_name' in path_user:
                            path_name = '%s%s' % (path_user['last_name'], path_user['name'])
                        else:
                            path_name = path_user['name']
                        path.append((path_name, path_user['mobile']['country_code'], path_user['mobile']['number']))
                else:
                    path = None
                row = dict(
                    content_name=ticket['content']['name'],
                    ticket_type_name=ticket['ticket_type']['name'],
                    ticket_type_desc=ticket['ticket_type']['desc']['value'],
                    status=ticket['status'],
                    path=str(path),
                    user_name=name,
                    user_mobile_country_code=ticket['receive_user']['mobile']['country_code'],
                    user_mobile_number=ticket['receive_user']['mobile']['number'],
                    birthday=birthday,
                    gender=gender
                )
                writer.writerow(row)
            pprint(len(tickets))

    else:
        click.secho('check parameters <python export.py  --help>', fg='red')


cli = click.CommandCollection(sources=[group_ticket, user_ticket, report_ticket, use_ticket])


if __name__ == '__main__':
    cli()
