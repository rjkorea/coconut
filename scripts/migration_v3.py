# -*- coding: utf-8 -*-

from pprint import pprint
import click
from pymongo import MongoClient
from datetime import datetime


@click.group()
def user_name():
    pass

@user_name.command()
@click.option('-m', '--mongo', default='localhost:27017', help='host of mongodb')
@click.option('--dryrun', is_flag=True, help='dry run test')
@click.confirmation_option(help='Are you sure your migration?')
def user_names(mongo, dryrun):
    click.secho('= params info =', fg='cyan')
    click.secho('mongodb: %s' % (mongo), fg='green')
    click.secho('dry run test %s' % dryrun, fg='red')
    if mongo:
        mongo_client = MongoClient(host=mongo.split(':')[0], port=int(mongo.split(':')[1]))
        cursor = mongo_client['coconut']['user'].find({}, {'_id': True, 'name': True, 'last_name': True})
        while cursor.alive:
            user = cursor.next()
            if dryrun:
                pprint(user)
            else:
                if 'last_name' in user:
                    doc = {
                        '$set': {
                            'name': '%s %s' % (user['last_name'], user['name'])
                        },
                        '$unset': {
                            'last_name': 1
                        }
                    }
                    mongo_client['coconut']['user'].update({'_id': user['_id']}, doc, False, False)
    else:
        pprint('invalid parameters')


@click.group()
def user_send_history():
    pass

@user_send_history.command()
@click.option('-m', '--mongo', default='localhost:27017', help='host of mongodb')
@click.option('--dryrun', is_flag=True, help='dry run test')
@click.confirmation_option(help='Are you sure your migration?')
def user_send_histories(mongo, dryrun):
    click.secho('= params info =', fg='cyan')
    click.secho('mongodb: %s' % (mongo), fg='green')
    click.secho('dry run test %s' % dryrun, fg='red')
    if mongo:
        mongo_client = MongoClient(host=mongo.split(':')[0], port=int(mongo.split(':')[1]))
        cursor = mongo_client['coconut']['ticket_log'].find({'action': 'send'}).sort([('created_at', 1)])
        while cursor.alive:
            ticket_log = cursor.next()
            receive_user = mongo_client['coconut']['user'].find_one({'_id': ticket_log['receive_user_oid']})
            if receive_user and 'name' in receive_user and 'mobile' in receive_user:
                query = {
                    'user_oid': ticket_log['send_user_oid'],
                    'name': receive_user['name'],
                    'mobile.country_code': receive_user['mobile']['country_code'],
                    'mobile.number': receive_user['mobile']['number']
                }
                set_doc = {
                    'user_oid': ticket_log['send_user_oid'],
                    'name': receive_user['name'],
                    'mobile': receive_user['mobile'],
                    'enabled': True,
                    'created_at': ticket_log['created_at'],
                    'updated_at': ticket_log['updated_at']
                }
            if dryrun:
                pprint(set_doc)
            else:
                mongo_client['coconut']['user_send_history'].update(query, set_doc, True, False)
    else:
        pprint('invalid parameters')


if __name__ == '__main__':
    cli = click.CommandCollection(name='migration_v3', sources=[user_name, user_send_history])
    cli()
