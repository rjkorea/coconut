# -*- coding: utf-8 -*-

from datetime import datetime
from bson import ObjectId

import csv
import click
from pymongo import MongoClient


@click.group()
def invitation():
    pass

@invitation.command()
@click.option('-c', '--csvfile', help='csv filename')
@click.option('-m', '--mongo', default='localhost:27017', help='host of mongodb')
@click.option('--dryrun', is_flag=True, help='dry run test')
@click.confirmation_option(help='Are you sure you want to mongodb?')
def invitations(csvfile, mongo, dryrun):
    click.secho('= params info =', fg='cyan')
    click.secho('csvfile: %s' % (csvfile), fg='green')
    click.secho('mongodb: %s' % (mongo), fg='green')
    if csvfile and mongo:
        mongo_client = MongoClient(host=mongo.split(':')[0], port=int(mongo.split(':')[1]))
        res = csv.DictReader(open(csvfile, 'r'))
        for line in res:
            line['mobile_number'] = line['mobile_number'].replace('-', '').replace('\u200b', '').replace(' ', '')
            line['created_at'] = datetime.utcnow()
            line['updated_at'] = datetime.utcnow()
            line['enabled'] = True
            line['entered'] = False
            if line['gender'] == '':
                line['gender'] = 'female'
            if line['gender'] == '여':
                line['gender'] = 'female'
            if line['gender'] == '남':
                line['gender'] = 'male'
            if line['fee'] == 'X':
                line['fee'] = dict(enabled=False)
            elif line['fee'] == 'O':
                line['fee'] = dict(enabled=True, method='cash', price=10000)
            if dryrun:
                print(line)
            else:
                mongo_client['coconut']['invitation'].insert(line)
    else:
        click.secho('check parameters <python import.py invitations --help>', fg='red')


@click.group()
def ticket():
    pass

@ticket.command()
@click.option('-c', '--csvfile', help='csv filename')
@click.option('-m', '--mongo', default='localhost:27017', help='host of mongodb')
@click.option('-i', '--contentid', help='host of mongodb')
@click.option('--dryrun', is_flag=True, help='dry run test')
@click.confirmation_option(help='Are you sure you want to mongodb?')
def tickets(csvfile, mongo, contentid, dryrun):
    click.secho('= params info =', fg='cyan')
    click.secho('csvfile: %s' % (csvfile), fg='green')
    click.secho('mongodb: %s' % (mongo), fg='green')
    if csvfile and mongo and contentid:
        mongo_client = MongoClient(host=mongo.split(':')[0], port=int(mongo.split(':')[1]))
        res = csv.DictReader(open(csvfile, 'r'))
        for line in res:
            line['created_at'] = datetime.utcnow()
            line['updated_at'] = datetime.utcnow()
            line['enabled'] = True
            line['status'] = 'register'
            if line['gender'] == '':
                line['gender'] = ''
            if line['gender'] == '여자':
                line['gender'] = 'female'
            if line['gender'] == '남자':
                line['gender'] = 'male'
            line['days'] = [{
                'day': 1,
                'entered': False
            }]
            if line['fee'] == 'O':
                line['days'][0]['fee'] = dict(method='cash', price=10000)
            line.pop('fee')

            # TODO birthday

            # TODO add user_oid
            line['mobile_number'] = '82'+line['mobile_number'].replace('-', '').replace('\u200b', '').replace(' ', '')[1:]
            user = mongo_client['coconut']['user'].find_one({'mobile_number': line['mobile_number']})
            if not user:
                user = {
                    'name': line['name'],
                    'mobile_number': line['mobile_number'],
                    'gender': line['gender'],
                    'birthday': line['birthday'],
                    'enabled': True,
                    'created_at': datetime.utcnow(),
                    'updated_at': datetime.utcnow()
                }
                line['user_oid'] = mongo_client['coconut']['user'].insert(user)
            else:
                line['user_oid'] = user['_id']
            line.pop('name')
            line.pop('mobile_number')
            line.pop('gender')
            line.pop('birthday')

            # TODO add empty ticket_order_oid
            line['ticket_order_oid'] = None
            
            # TODO add ticket_type_oid
            line['ticket_type_oid'] = mongo_client['coconut']['ticket_type'].find_one({'name': line['ticket_type']})['_id']
            line.pop('ticket_type')

            # TODO add content_oid
            line['content_oid'] = ObjectId(contentid)

            if dryrun:
                print(line)
            else:
                mongo_client['coconut']['ticket'].insert(line)
    else:
        click.secho('check parameters <python import.py  --help>', fg='red')


@click.group()
def group_ticket():
    pass

@group_ticket.command()
@click.option('-c', '--csvfile', help='csv filename')
@click.option('-m', '--mongo', default='localhost:27017', help='host of mongodb')
@click.option('-a', '--adminid', help='admin id')
@click.option('-i', '--contentid', help='content id')
@click.option('--dryrun', is_flag=True, help='dry run test')
@click.confirmation_option(help='Are you sure you import to mongodb?')
def group_tickets(csvfile, mongo, contentid, adminid, dryrun):
    click.secho('= params info =', fg='cyan')
    click.secho('csvfile: %s' % (csvfile), fg='green')
    click.secho('mongodb: %s' % (mongo), fg='green')
    now = datetime.utcnow()
    if csvfile and mongo and contentid and adminid:
        mongo_client = MongoClient(host=mongo.split(':')[0], port=int(mongo.split(':')[1]))
        res = csv.DictReader(open(csvfile, 'r'))
        for i, line in enumerate(res):
            group = mongo_client['coconut']['group'].find_one(
                {
                    'content_oid': ObjectId(contentid),
                    'name': line['group_name'],
                    'desc': line['group_desc']
                }
            )
            if group:
                doc = {
                    'group_oid': group['_id'],
                    'content_oid': ObjectId(contentid),
                    'enabled': True,
                    'used': False,
                    'name': line['name'],
                    'mobile_number': line['mobile_number'],
                    'created_at': now,
                    'updated_at': now
                }
                group_ticket_id = mongo_client['coconut']['group_ticket'].insert(doc)
                print('%d: gt_id: %s' % (i, group_ticket_id))
                mongo_client['coconut']['group'].update({'_id': group['_id']}, {'$inc': {'qty': 1}})
            else:
                doc = {
                    'admin_oid': ObjectId(adminid),
                    'content_oid': ObjectId(contentid),
                    'name': line['group_name'],
                    'desc': line['group_desc'],
                    'qty': 0,
                    'enabled': True,
                    'created_at': now,
                    'updated_at': now
                }
                group_id = mongo_client['coconut']['group'].insert(doc)
                doc = {
                    'group_oid': ObjectId(group_id),
                    'content_oid': ObjectId(contentid),
                    'enabled': True,
                    'used': False,
                    'name': line['name'],
                    'mobile_number': line['mobile_number'],
                    'created_at': now,
                    'updated_at': now
                }
                group_ticket_id = mongo_client['coconut']['group_ticket'].insert(doc)
                print('%d: g_id: %s, gt_id: %s' % (i, group_id, group_ticket_id))
                mongo_client['coconut']['group'].update({'_id': ObjectId(group_id)}, {'$inc': {'qty': 1}})
    else:
        click.secho('check parameters <python import.py  --help>', fg='red')


cli = click.CommandCollection(sources=[invitation, ticket, group_ticket])


if __name__ == '__main__':
    cli()
