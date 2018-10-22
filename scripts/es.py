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


@click.group()
def ticket():
    pass

def tickets_orig(mongo, es, type, start, end, chunk):
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
            cur = mongo_client['coconut']['ticket'].find(create_query(type, start, end))
            click.secho('= log =', fg='cyan')

            i = -1                  # If document not exist, it occurs 'UnboundLocalError'
            for i, (ok, result) in enumerate(
                    streaming_bulk(client=es_client, actions=add_tickets_index(cur, mongo_client), index='tickets',
                                   doc_type='ticket', chunk_size=chunk)):
                click.secho(str(result), fg='green')
            end_time = datetime.today()
            click.secho('= result =', fg='cyan')
            click.secho('indexed documents: %d' % (i + 1), fg='green')
            click.secho('start time: %s' % start_time, fg='green')
            click.secho('end time: %s' % end_time, fg='green')
            click.secho('elapsed time: %s' % str(end_time - start_time), fg='green')
    else:
        click.secho('check parameters <python es.py tickets --help>', fg='red')


@ticket.command()
@click.option('-m', '--mongo', default='localhost:27017', help='host of mongodb')
@click.option('--es', default='localhost:9200', help='host of elasticsearch')
@click.option('-t', '--type', type=click.Choice(['created_at', 'updated_at']), help='select date type')
@click.option('-s', '--start', help='start date [YYYY-MM-DD]')
@click.option('-e', '--end', help='end date [YYYY-MM-DD]')
@click.option('-c', '--chunk', default=10, help='number of chunk data')
@click.confirmation_option(help='Are you sure you want to index the db?')
def tickets(mongo, es, type, start, end, chunk):
    "Index invitations from mongodb to elasticsearch"
    # For calling original method
    tickets_orig(mongo, es, type, start, end, chunk)


def add_tickets_index(cursor, mongo_client):
    for c in cursor:
        yield gen_ticket(c, mongo_client)


def gen_ticket(cursor, mongo_client):
    ticket = dict(
        _id=str(cursor['_id']),
        enabled=cursor['enabled'],
        content_oid=str(cursor['content_oid']),
        ticket_type_oid=str(cursor['ticket_type_oid']),
        status=cursor['status'],
        created_at=cursor['created_at'].strftime('%Y-%m-%dT%H:%M:%S+0000'),
        updated_at=cursor['updated_at'].strftime('%Y-%m-%dT%H:%M:%S+0000'),
    )
    if 'receive_user_oid' in cursor:
        ticket['receive_user_oid'] = str(cursor['receive_user_oid'])
        receive_user = mongo_client['coconut']['user'].find_one({'_id': cursor['receive_user_oid']})
        if 'gender' in receive_user:
            ticket['receive_user_gender'] = receive_user['gender']
        if 'birthday' in receive_user:
            ticket['receive_user_birthday'] = receive_user['birthday'][:2]
    if 'ticket_order_oid' in cursor:
        ticket['ticket_order_oid'] = str(cursor['ticket_order_oid'])
    if 'fee' in cursor['days'][0]:
        ticket['price'] = cursor['days'][0]['fee']['price']
    content = mongo_client['coconut']['content'].find_one({'_id': cursor['content_oid']})
    ticket['content_name'] = content['name']
    ticket_type = mongo_client['coconut']['ticket_type'].find_one({'_id': cursor['ticket_type_oid']})
    ticket['ticket_type_name'] = ticket_type['name']
    ticket['ticket_type_desc'] = ticket_type['desc']['value']
    return ticket


@click.group()
def user():
    pass

def users_orig(mongo, es, type, start, end, chunk):
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
            cur = mongo_client['coconut']['user'].find(create_query(type, start, end))
            click.secho('= log =', fg='cyan')
            i = -1                  # If document not exist, it occurs 'UnboundLocalError'
            for i, (ok, result) in enumerate(
                    streaming_bulk(client=es_client, actions=add_users_index(cur), index='users',
                                   doc_type='user', chunk_size=chunk)):
                click.secho(str(result), fg='green')
            end_time = datetime.today()
            click.secho('= result =', fg='cyan')
            click.secho('indexed documents: %d' % (i + 1), fg='green')
            click.secho('start time: %s' % start_time, fg='green')
            click.secho('end time: %s' % end_time, fg='green')
            click.secho('elapsed time: %s' % str(end_time - start_time), fg='green')
    else:
        click.secho('check parameters <python es.py users --help>', fg='red')


@user.command()
@click.option('-m', '--mongo', default='localhost:27017', help='host of mongodb')
@click.option('--es', default='localhost:9200', help='host of elasticsearch')
@click.option('-t', '--type', type=click.Choice(['created_at', 'updated_at']), help='select date type')
@click.option('-s', '--start', help='start date [YYYY-MM-DD]')
@click.option('-e', '--end', help='end date [YYYY-MM-DD]')
@click.option('-c', '--chunk', default=10, help='number of chunk data')
@click.confirmation_option(help='Are you sure you want to index the db?')
def users(mongo, es, type, start, end, chunk):
    "Index users from mongodb to elasticsearch"
    # For calling original method
    users_orig(mongo, es, type, start, end, chunk)


def add_users_index(cursor):
    for c in cursor:
        yield gen_user(c)


def gen_user(cursor):
    user = dict(
        _id=str(cursor['_id']),
        mobile_number=cursor['mobile_number'],
        enabled=cursor['enabled'],
        created_at=cursor['created_at'].strftime('%Y-%m-%dT%H:%M:%S+0000'),
    )
    if 'birthday' in cursor and cursor['birthday'].strip():
        if len(cursor['birthday'].strip()) == 8:
            user['birthday'] = str(cursor['birthday'])
            user['age'] = 2018-int(user['birthday'][:4])
        elif len(cursor['birthday'].strip()) == 6:
            if cursor['birthday'][0] == '0' or cursor['birthday'][0] == '1':
                user['birthday'] = '20%s' % cursor['birthday']
            else:
                user['birthday'] = '19%s' % cursor['birthday']
            user['age'] = 2018-int(user['birthday'][:4])
    if 'gender' in cursor:
        user['gender'] = str(cursor['gender'])
    return user



@click.group()
def ticket_log():
    pass

def ticket_logs_orig(mongo, es, type, start, end, chunk):
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
            cur = mongo_client['coconut']['ticket_log'].find(create_query(type, start, end))
            click.secho('= log =', fg='cyan')

            i = -1                  # If document not exist, it occurs 'UnboundLocalError'
            for i, (ok, result) in enumerate(
                    streaming_bulk(client=es_client, actions=add_ticket_logs_index(cur, mongo_client), index='ticket_logs',
                                   doc_type='ticket_log', chunk_size=chunk)):
                click.secho(str(result), fg='green')
            end_time = datetime.today()
            click.secho('= result =', fg='cyan')
            click.secho('indexed documents: %d' % (i + 1), fg='green')
            click.secho('start time: %s' % start_time, fg='green')
            click.secho('end time: %s' % end_time, fg='green')
            click.secho('elapsed time: %s' % str(end_time - start_time), fg='green')
    else:
        click.secho('check parameters <python es.py ticket_logs --help>', fg='red')


@ticket_log.command()
@click.option('-m', '--mongo', default='localhost:27017', help='host of mongodb')
@click.option('--es', default='localhost:9200', help='host of elasticsearch')
@click.option('-t', '--type', type=click.Choice(['created_at', 'updated_at']), help='select date type')
@click.option('-s', '--start', help='start date [YYYY-MM-DD]')
@click.option('-e', '--end', help='end date [YYYY-MM-DD]')
@click.option('-c', '--chunk', default=10, help='number of chunk data')
@click.confirmation_option(help='Are you sure you want to index the db?')
def ticket_logs(mongo, es, type, start, end, chunk):
    "Index ticket logs from mongodb to elasticsearch"
    # For calling original method
    ticket_logs_orig(mongo, es, type, start, end, chunk)


def add_ticket_logs_index(cursor, mongo_client):
    for c in cursor:
        yield gen_ticket_log(c, mongo_client)


def gen_ticket_log(cursor, mongo_client):
    ticket_log = dict(
        _id=str(cursor['_id']),
        content_oid=str(cursor['content_oid']),
        action=cursor['action'],
        created_at=cursor['created_at'].strftime('%Y-%m-%dT%H:%M:%S+0000')
    )
    if 'receive_user_oid' in cursor:
        ticket_log['receive_user_oid'] = str(cursor['receive_user_oid'])
        receive_user = mongo_client['coconut']['user'].find_one({'_id': cursor['receive_user_oid']})
        if receive_user:
            if 'gender' in receive_user:
                ticket_log['receive_user_gender'] = receive_user['gender']
            if 'birthday' in receive_user:
                ticket_log['receive_user_birthday'] = receive_user['birthday'][:2]
    if 'send_user_oid' in cursor:
        ticket_log['send_user_oid'] = str(cursor['send_user_oid'])
        send_user = mongo_client['coconut']['user'].find_one({'_id': cursor['send_user_oid']})
        if send_user:
            if 'gender' in send_user:
                ticket_log['send_user_gender'] = send_user['gender']
            if 'birthday' in send_user:
                ticket_log['send_user_birthday'] = send_user['birthday'][:2]
    content = mongo_client['coconut']['content'].find_one({'_id': cursor['content_oid']})
    ticket_log['content_name'] = content['name']
    return ticket_log


cli = click.CommandCollection(sources=[invitation, ticket, user, ticket_log])

if __name__ == '__main__':
    cli()
