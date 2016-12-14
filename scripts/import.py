# -*- coding: utf-8 -*-

from datetime import datetime

import csv
import click
from pymongo import MongoClient


@click.group()
def invitation():
    pass


@invitation.command()
@click.option('-c', '--csvfile', help='csv filename')
@click.option('-m', '--mongo', default='localhost:27017', help='host of mongodb')
@click.confirmation_option(help='Are you sure you want to mongodb?')
def invitations(csvfile, mongo):
    click.secho('= params info =', fg='cyan')
    click.secho('csvfile: %s' % (csvfile), fg='green')
    click.secho('mongodb: %s' % (mongo), fg='green')
    if csvfile and mongo:
        mongo_client = MongoClient(host=mongo.split(':')[0], port=int(mongo.split(':')[1]))
        res = csv.DictReader(open(csvfile, 'r'))
        for line in res:
            line['mobile_number'] = line['mobile_number'].replace('-', '')
            line['created_at'] = datetime.utcnow()
            line['updated_at'] = datetime.utcnow()
            line['enabled'] = True
            line['entered'] = False
            if line['fee'] == 'X':
                line['fee'] = dict(enabled=False)
            elif line['fee'] == 'O':
                line['fee'] = dict(enabled=True)
            mongo_client['coconut']['invitation'].insert(line)
            print(line)
    else:
        click.secho('check parameters <python import.py invitations --help>', fg='red')


cli = click.CommandCollection(sources=[invitation])


if __name__ == '__main__':
    cli()
