# -*- coding: utf-8 -*-

from pprint import pprint
import click
from pymongo import MongoClient

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


if __name__ == '__main__':
    cli = click.CommandCollection(name='migration_v2', sources=[content])
    cli()
