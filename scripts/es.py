# -*- coding: utf-8 -*-

import re
import pytz
from datetime import datetime

import click
from elasticsearch import Elasticsearch
from elasticsearch.helpers import streaming_bulk
from pymongo import MongoClient


def create_query(type, start, end):
    if type == 'created_at':
        return {
            'created_at': {
                '$gte': datetime.strptime(start, '%Y-%m-%d'),
                '$lt': datetime.strptime(end, '%Y-%m-%d')
            }
        }
    elif type == 'updated_at':
        return {
            'updated_at': {
                '$gte': datetime.strptime(start, '%Y-%m-%d'),
                '$lt': datetime.strptime(end, '%Y-%m-%d')
            }
        }
    else:
        return None


@click.group()
def invitation():
    pass


def invitations_orig(mongo, es, type, start, end, chunk):
    click.secho('= params info =', fg='cyan')
    click.secho('mongodb: %s' % (mongo), fg='green')
    click.secho('elasticsearch: %s' % (es), fg='green')
    click.secho('date type: %s' % (type), fg='green')
    click.secho('start date: %s' % (start), fg='green')
    click.secho('end date: %s' % (end), fg='green')
    click.secho('chunk: %d' % (chunk), fg='green')
    if mongo and es and type and start and end and chunk:
        try:
            datetime.strptime(start, '%Y-%m-%d')
            datetime.strptime(end, '%Y-%m-%d')
        except ValueError as e:
            click.secho(str(e), fg='red')
            return -1
        else:
            start_time = datetime.today()
            es_client = Elasticsearch(hosts=[es])
            mongo_client = MongoClient(host=mongo.split(':')[0], port=int(mongo.split(':')[1]))
            cur = mongo_client['coconut']['invitation'].find(create_query(type, start, end))
            click.secho('= log =', fg='cyan')

            i = -1                  # If document not exist, it occurs 'UnboundLocalError'
            for i, (ok, result) in enumerate(
                    streaming_bulk(client=es_client, actions=add_invitations_index(cur), index='invitations',
                                   doc_type='invitation', chunk_size=chunk)):
                click.secho(str(result), fg='green')
            end_time = datetime.today()
            click.secho('= result =', fg='cyan')
            click.secho('indexed documents: %d' % (i + 1), fg='green')
            click.secho('start time: %s' % start_time, fg='green')
            click.secho('end time: %s' % end_time, fg='green')
            click.secho('elapsed time: %s' % str(end_time - start_time), fg='green')
    else:
        click.secho('check parameters <python es.py invitations --help>', fg='red')


@invitation.command()
@click.option('-m', '--mongo', default='localhost:27017', help='host of mongodb')
@click.option('--es', default='localhost:9200', help='host of elasticsearch')
@click.option('-t', '--type', type=click.Choice(['created_at', 'updated_at']), help='select date type')
@click.option('-s', '--start', help='start date [YYYY-MM-DD]')
@click.option('-e', '--end', help='end date [YYYY-MM-DD]')
@click.option('-c', '--chunk', default=10, help='number of chunk data')
@click.confirmation_option(help='Are you sure you want to index the db?')
def invitations(mongo, es, type, start, end, chunk):
    "Index invitations from mongodb to elasticsearch"
    # For calling original method
    invitations_orig(mongo, es, type, start, end, chunk)


def add_invitations_index(cursor):
    for c in cursor:
        yield gen_invitation(c)


def gen_invitation(cursor):
    invitation = dict(
            _id=str(cursor['_id']),
            enabled=cursor['enabled'],
            mobile_number=cursor['mobile_number'],
            name=cursor['name'],
            type=cursor['type'],
            email=cursor['email'],
            entered=cursor['entered'],
            assignee=cursor['assignee'],
            fee=dict(
                    enabled=cursor['fee']['enabled'],
            ),
            created_at=cursor['created_at'].strftime('%Y-%m-%dT%H:%M:%S+0000'),
            updated_at=cursor['updated_at'].strftime('%Y-%m-%dT%H:%M:%S+0000'),
            weekday_at=cursor['updated_at'].weekday(),
            hour_at=cursor['updated_at'].hour
    )
    if 'quantity' in cursor:
        invitation['quantity'] = cursor['quantity']
    if cursor['fee']['enabled']:
        if 'method' in cursor['fee']:
            invitation['fee']['method'] = cursor['fee']['method']
        if 'price' in cursor['fee']:
            if cursor['fee']['price']:
                invitation['fee']['price'] = int(cursor['fee']['price'])

    if cursor['gender'].strip() == '여' or cursor['gender'].strip() == 'female':
        invitation['gender'] = 'female'
    elif cursor['gender'].strip() == '남' or cursor['gender'].strip() == 'male':
        invitation['gender'] = 'male'

    if cursor['group'].strip() == '일반 게스트':
        invitation['group'] = '일반게스트'
    elif cursor['group'].strip() == 'RJ Ent. 일반 게스트':
        invitation['group'] = 'RJ Ent. 일반게스트'
    elif cursor['group'].strip() == 'RJ Ent.':
        invitation['group'] = 'RJ Ent. 일반게스트'
    else:
        invitation['group'] = cursor['group'].strip()

    if cursor['birthday'] and len(cursor['birthday'].strip().replace(' ', '').replace('.', '')) == 6:
        invitation['birthday'] = int('19%s' % cursor['birthday'][:2])
        invitation['age'] = 2017-invitation['birthday']
    return invitation


cli = click.CommandCollection(sources=[invitation])

if __name__ == '__main__':
    cli()
