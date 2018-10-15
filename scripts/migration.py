# -*- coding: utf-8 -*-

from datetime import datetime
from bson import ObjectId
from pprint import pprint

import click
from pymongo import MongoClient


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
    if mongo:
        mongo_client = MongoClient(host=mongo.split(':')[0], port=int(mongo.split(':')[1]))
        cursor = mongo_client['coconut']['ticket_type'].find({})
        while cursor.alive:
            doc = cursor.next()
            if 'desc' in doc:
                set = {
                    '$set': {
                        'desc': {
                            'enabled': True,
                            'value': doc['desc']
                        }
                    }
                }
            else:
                set = {
                    '$set': {
                        'desc': {
                            'enabled': False,
                            'value': ''
                        }
                    }
                }
            if dryrun:
                pprint(doc)
                pprint(set)
            else:
                mongo_client['coconut']['ticket_type'].update({'_id': doc['_id']}, set, False, False)
    else:
        click.secho('check parameters <python migration.py --help>', fg='red')


@click.group()
def birthday():
    pass

@birthday.command()
@click.option('-m', '--mongo', default='localhost:27017', help='host of mongodb')
@click.option('--dryrun', is_flag=True, help='dry run test')
@click.confirmation_option(help='Are you sure your migration?')
def birthdays(mongo, dryrun):
    click.secho('= params info =', fg='cyan')
    click.secho('mongodb: %s' % (mongo), fg='green')
    if mongo:
        mongo_client = MongoClient(host=mongo.split(':')[0], port=int(mongo.split(':')[1]))
        cursor = mongo_client['coconut']['user'].find({})
        while cursor.alive:
            doc = cursor.next()
            set = dict()
            if 'birthday' in doc and len(doc['birthday'].strip()) == 8:
                set = {
                    '$set': {
                        'birthday': doc['birthday']
                    }
                }
            elif 'birthday' in doc and len(doc['birthday'].strip()) == 6:
                if doc['birthday'][0] == '0' or doc['birthday'][0] =='1':
                    set = {
                        '$set': {
                            'birthday': '20%s' % doc['birthday']
                        }
                    }
                else:
                    set = {
                        '$set': {
                            'birthday': '19%s' % doc['birthday']
                        }
                    }
            if dryrun:
                pprint(set)
            else:
                mongo_client['coconut']['user'].update({'_id': doc['_id']}, set, False, False)
    else:
        click.secho('check parameters <python migration.py --help>', fg='red')


cli = click.CommandCollection(sources=[ticket_type, birthday])


if __name__ == '__main__':
    cli()
