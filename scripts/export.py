# -*- coding: utf-8 -*-

from datetime import datetime
from bson import ObjectId
from pprint import pprint

import csv
import click
from pymongo import MongoClient


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
def user_tickets(csvfile, mongo, contentid, status, fee, dryrun):
    click.secho('= params info =', fg='cyan')
    click.secho('csvfile: %s' % (csvfile), fg='green')
    click.secho('mongodb: %s' % (mongo), fg='green')
    now = datetime.utcnow()
    if csvfile and mongo and contentid and status:
        fieldnames = ['name', 'mobile_number']
        writer = csv.writer(open(csvfile, 'w'))
        mongo_client = MongoClient(host=mongo.split(':')[0], port=int(mongo.split(':')[1]))
        ticket_orders = mongo_client['coconut']['ticket_order'].find({'content_oid': ObjectId(contentid), 'fee.price': {'$exists': True}}, [('_id')])
        if fee:
            cursor = mongo_client['coconut']['ticket'].find({'content_oid': ObjectId(contentid), 'status': status, 'ticket_order_oid': {'$in': [to['_id'] for to in ticket_orders]}})
        else:
            cursor = mongo_client['coconut']['ticket'].find({'content_oid': ObjectId(contentid), 'status': status})
        users_map = dict()
        while cursor.alive:
            doc = cursor.next()
            user = mongo_client['coconut']['user'].find_one({'_id': doc['receive_user_oid']})
            users_map[user['mobile_number']] = user['name']
        if dryrun:
            pprint(users_map)
        else:
            for user in users_map.items():
                writer.writerow([user[0].replace('8210', '010'), user[1]])
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
    now = datetime.utcnow()
    if csvfile and mongo:
        fieldnames = ['content_name', 'ticket_type_name', 'ticket_type_desc', 'price', 'status', 'user_name', 'user_mobile_number']
        writer = csv.DictWriter(open(csvfile, 'w'), fieldnames=fieldnames)
        writer.writeheader()
        mongo_client = MongoClient(host=mongo.split(':')[0], port=int(mongo.split(':')[1]))
        if contentid:
            q = { 'content_oid': ObjectId(contentid) }
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
            receive_user = mongo_client['coconut']['user'].find_one({'_id': doc['receive_user_oid']}, {'_id': 0, 'name': 1, 'mobile_number': 1})
            doc['receive_user'] = receive_user
            tickets.append(doc)
        if dryrun:
            pprint(tickets)
            pprint(len(tickets))
        else:
            for ticket in tickets   :
                row = dict(
                    content_name=ticket['content']['name'],
                    ticket_type_name=ticket['ticket_type']['name'],
                    ticket_type_desc=ticket['ticket_type']['desc']['value'],
                    price=0,
                    status=ticket['status'],
                    user_name=ticket['receive_user']['name'],
                    user_mobile_number=ticket['receive_user']['mobile_number']
                )
                if 'fee' in ticket['days'][0]:
                    row['price'] = ticket['days'][0]['fee']['price']
                writer.writerow(row)
            pprint(len(tickets))

    else:
        click.secho('check parameters <python export.py  --help>', fg='red')

cli = click.CommandCollection(sources=[group_ticket, user_ticket, report_ticket])


if __name__ == '__main__':
    cli()
