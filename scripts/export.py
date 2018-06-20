# -*- coding: utf-8 -*-

from datetime import datetime
from bson import ObjectId

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
@click.confirmation_option(help='Are you sure you import to mongodb?')
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
                name=doc['name'],
                mobile_number=doc['mobile_number'],
                used=doc['used']
            )
            writer.writerow(row)
    else:
        click.secho('check parameters <python export.py  --help>', fg='red')


cli = click.CommandCollection(sources=[group_ticket])


if __name__ == '__main__':
    cli()
