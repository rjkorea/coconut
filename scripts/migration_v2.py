# -*- coding: utf-8 -*-

from pprint import pprint
import click
from pymongo import MongoClient
from datetime import datetime


@click.group()
def content():
    pass

@content.command()
@click.option('-m', '--mongo', default='localhost:27017', help='host of mongodb')
@click.option('--dryrun', is_flag=True, help='dry run test')
@click.confirmation_option(help='Are you sure your migration?')
def contents(mongo, dryrun):
    click.secho('= params info =', fg='cyan')
    click.secho('mongodb: %s' % (mongo), fg='green')
    click.secho('dry run test %s' % dryrun, fg='red')
    if mongo:
        mongo_client = MongoClient(host=mongo.split(':')[0], port=int(mongo.split(':')[1]))
        cursor = mongo_client['coconut']['content'].find({})
        while cursor.alive:
            content = cursor.next()
            set = {
                'is_private': False,
                'site_url': None,
                'video_url': None,
                'host': {
                    'name': None,
                    'tel': None,
                    'email': None
                },
                'comments': {
                    'type': 'guestbook',
                    'is_private': False
                },
                'place': {
                    'name': content['place'],
                    'url': None,
                    'x': None,
                    'y': None
                },
                'images': [
                    {
                        'm': content['image']['poster']['m']
                    },
                    {
                        'm': content['image']['extra'][0]['m']
                    },
                    {
                        'm': content['image']['extra'][1]['m']
                    },
                    {
                        'm': content['image']['extra'][2]['m']
                    },
                    {
                        'm': content['image']['extra'][3]['m']
                    },
                    {
                        'm': content['image']['extra'][4]['m']
                    }
                ]
            }
            admin = mongo_client['coconut']['admin'].find_one({'_id': content['admin_oid']})
            if 'type' not in admin or admin['type'] == 'personal':
                if 'last_name' in admin:
                    set['host']['name'] = '%s%s' % (admin['last_name'], admin['name'])
                else:
                    set['host']['name'] = admin['name']
                set['host']['email'] = admin['email']
                set['host']['tel'] = admin['mobile_number']
            elif admin['type'] == 'business':
                set['host']['name'] = admin['name']
                set['host']['email'] = admin['email']
                set['host']['tel'] = admin['tel']
            unset = {
                'image': 1
            }
            if dryrun:
                pprint(content['name'])
                pprint(set)
                pprint(unset)
            else:
                set_doc = {
                    '$set': set,
                    '$unset': unset
                }
                mongo_client['coconut']['content'].update({'_id': content['_id']}, set_doc, False, False)


@click.group()
def ticket_type():
    pass

@ticket_type.command()
@click.option('-m', '--mongo', default='localhost:27017', help='host of mongodb')
@click.option('--dryrun', is_flag=True, help='dry run test')
@click.confirmation_option(help='Are you sure your migration?')
def ticket_types(mongo, dryrun):
    click.secho('= params info =', fg='cyan')
    click.secho('mongodb: %s' % (mongo), fg='green')
    click.secho('dry run test %s' % dryrun, fg='red')
    if mongo:
        mongo_client = MongoClient(host=mongo.split(':')[0], port=int(mongo.split(':')[1]))
        cursor = mongo_client['coconut']['ticket_type'].find({}, sort=[('created_at', 1)])
        while cursor.alive:
            set = dict()
            unset = dict()
            ticket_type = cursor.next()
            if 'expiry_date' in ticket_type:
                set['sales'] = {
                    'end': ticket_type['expiry_date']
                }
                unset['expiry_date'] = 1
            if 'duplicated_registration' not in ticket_type:
                set['duplicated_registration'] = False
            if 'color' not in ticket_type:
                set['color'] = 'tkit-mint'
            if 'color' in ticket_type and isinstance(ticket_type['color'], dict):
                set['color'] = ticket_type['color']['name']
            if 'day' in ticket_type:
                unset['day'] = 1
            set_doc = {
                '$set': set,
                '$unset': unset
            }
            if dryrun:
                pprint(ticket_type)
                pprint(set_doc)
            else:
                set_doc = dict()
                if set:
                    set_doc['$set'] = set
                if unset:
                    set_doc['$unset'] = unset
                mongo_client['coconut']['ticket_type'].update({'_id': ticket_type['_id']}, set_doc, False, False)
        pprint(cursor.count())


# local working
@click.group()
def viral_ticket_count():
    pass

@viral_ticket_count.command()
@click.option('-m', '--mongo', default='localhost:27017', help='host of mongodb')
@click.option('--dryrun', is_flag=True, help='dry run test')
@click.confirmation_option(help='Are you sure your migration?')
def viral_ticket_counts(mongo, dryrun):
    click.secho('= params info =', fg='cyan')
    click.secho('mongodb: %s' % (mongo), fg='green')
    click.secho('dry run test %s' % dryrun, fg='red')
    if mongo:
        mongo_client = MongoClient(host=mongo.split(':')[0], port=int(mongo.split(':')[1]))
        cursor = mongo_client['test_database']['ticket_etl'].find({})
        stats = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0}
        while cursor.alive:
            ticket = cursor.next()
            if 'history_send_user_oids' in ticket:
                stats[len(ticket['history_send_user_oids'])] = stats[len(ticket['history_send_user_oids'])] + 1
        pprint(cursor.count())
        pprint(stats)


# local working
@click.group()
def none_user():
    pass

@none_user.command()
@click.option('-m', '--mongo', default='localhost:27017', help='host of mongodb')
@click.option('--dryrun', is_flag=True, help='dry run test')
@click.confirmation_option(help='Are you sure your migration?')
def none_users(mongo, dryrun):
    click.secho('= params info =', fg='cyan')
    click.secho('mongodb: %s' % (mongo), fg='green')
    click.secho('dry run test %s' % dryrun, fg='red')
    if mongo:
        mongo_client = MongoClient(host=mongo.split(':')[0], port=int(mongo.split(':')[1]))
        cursor = mongo_client['test_database']['user_live'].find({})
        no_user_count = 0
        exist_user_count = 0
        while cursor.alive:
            no_user = cursor.next()
            if 'name' not in no_user:
                pprint(no_user)
                no_user_count = no_user_count + 1
                exist_user = mongo_client['test_database']['user_20181009'].find_one({'_id': no_user['_id']})
                if exist_user:
                    exist_user_count = exist_user_count + 1
                    pprint(exist_user)
                    mongo_client['test_database']['user_live'].update(
                        {'_id': no_user['_id']},
                        {
                            '$set': exist_user
                        },
                        False,
                        False
                    )
        pprint(cursor.count())
        pprint(no_user_count)
        pprint(exist_user_count)


# local working
@click.group()
def umf2018_user():
    pass

@umf2018_user.command()
@click.option('-m', '--mongo', default='localhost:27017', help='host of mongodb')
@click.option('--dryrun', is_flag=True, help='dry run test')
@click.confirmation_option(help='Are you sure your migration?')
def umf2018_users(mongo, dryrun):
    click.secho('= params info =', fg='cyan')
    click.secho('mongodb: %s' % (mongo), fg='green')
    click.secho('dry run test %s' % dryrun, fg='red')
    if mongo:
        mongo_client = MongoClient(host=mongo.split(':')[0], port=int(mongo.split(':')[1]))
        users = dict()
        cursor = mongo_client['test_database']['group_ticket'].find({})
        while cursor.alive:
            ticket = cursor.next()
            if 'name' in ticket and 'mobile_number' in ticket:
                users[ticket['mobile_number']] = ticket['name']
        result = dict()
        for k, v in users.items():
            if k.startswith('10'):
                result['82%s' % k] = v
            if k.startswith('010'):
                result['82%s' % k[1:]] = v
        pprint(result)
        pprint(len(result))
        exist_user_count = 0
        for k, v in result.items():
            user = mongo_client['test_database']['user_live'].find_one({'mobile_number': k})
            if not user:
                doc = dict(
                    name=v,
                    mobile_number=k,
                    enabled=True,
                    created_at=datetime.strptime('2018-06-07 00:00:00', '%Y-%m-%d %H:%M:%S'),
                    updated_at=datetime.strptime('2018-06-07 00:00:00', '%Y-%m-%d %H:%M:%S'),
                    terms=dict(
                        privacy=False,
                        policy=False
                    )
                )
                mongo_client['test_database']['user_live'].insert(doc)
                exist_user_count = exist_user_count + 1
        pprint(exist_user_count)


# local working
@click.group()
def tn_user():
    pass

@tn_user.command()
@click.option('-m', '--mongo', default='localhost:27017', help='host of mongodb')
@click.option('--dryrun', is_flag=True, help='dry run test')
@click.confirmation_option(help='Are you sure your migration?')
def tn_users(mongo, dryrun):
    click.secho('= params info =', fg='cyan')
    click.secho('mongodb: %s' % (mongo), fg='green')
    click.secho('dry run test %s' % dryrun, fg='red')
    if mongo:
        mongo_client = MongoClient(host=mongo.split(':')[0], port=int(mongo.split(':')[1]))
        count = 0
        cursor = mongo_client['test_database']['tn'].find({})
        while cursor.alive:
            ticket = cursor.next()
            if ticket['mobile_number']:
                mn = '82%s' % ticket['mobile_number'].replace('-', '').strip()[1:]
                user = mongo_client['test_database']['user_live'].find_one({'mobile_number': mn})
                if not user:
                    doc = dict(
                        name=ticket['name'],
                        mobile_number=mn,
                        enabled=True,
                        created_at=datetime.strptime('2018-05-21 00:00:00', '%Y-%m-%d %H:%M:%S'),
                        updated_at=datetime.strptime('2018-05-21 00:00:00', '%Y-%m-%d %H:%M:%S'),
                        terms=dict(
                            privacy=False,
                            policy=False
                        )
                    )
                    mongo_client['test_database']['user_live'].insert(doc)
                    count = count + 1
        pprint(count)


# local working
@click.group()
def tkit_kr_user():
    pass

@tkit_kr_user.command()
@click.option('-m', '--mongo', default='localhost:27017', help='host of mongodb')
@click.option('--dryrun', is_flag=True, help='dry run test')
@click.confirmation_option(help='Are you sure your migration?')
def tkit_kr_users(mongo, dryrun):
    click.secho('= params info =', fg='cyan')
    click.secho('mongodb: %s' % (mongo), fg='green')
    click.secho('dry run test %s' % dryrun, fg='red')
    if mongo:
        mongo_client = MongoClient(host=mongo.split(':')[0], port=int(mongo.split(':')[1]))
        count = 0
        cursor = mongo_client['test_database']['tkit_kr'].find({})
        while cursor.alive:
            ticket = cursor.next()
            if ticket['mobile_number']:
                mn = '82%s' % ticket['mobile_number'].replace('-', '').strip()[1:]
                user = mongo_client['test_database']['user_live'].find_one({'mobile_number': mn})
                if not user and len(mn) == 12:
                    doc = dict(
                        name=ticket['name'],
                        mobile_number=mn,
                        enabled=True,
                        created_at=ticket['created_at'],
                        updated_at=ticket['created_at'],
                        terms=dict(
                            privacy=False,
                            policy=False
                        )
                    )
                    mongo_client['test_database']['user_live'].insert(doc)
                    count = count + 1
        pprint(count)


if __name__ == '__main__':
    cli = click.CommandCollection(name='migration_v2', sources=[content, ticket_type, viral_ticket_count, none_user, umf2018_user, tn_user, tkit_kr_user])
    cli()
