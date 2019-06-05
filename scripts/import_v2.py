# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from bson import ObjectId

import csv
import json
import click
from pprint import pprint
from pymongo import MongoClient
from slacker import Slacker


@click.group()
def list_ticket():
    pass

@list_ticket.command()
@click.option('-c', '--csvfile', help='csv filename')
@click.option('-a', '--adminid', help='oid of admin')
@click.option('-i', '--contentid', help='oid of content')
@click.option('-e', '--end', help='end date [YYYY-MM-DDTHH:MM:SS]')
@click.option('-m', '--mongo', default='localhost:27017', help='host of mongodb')
@click.option('--dryrun', is_flag=True, help='dry run test')
@click.confirmation_option(help='Are you sure you import ticket to mongodb?')
def list_tickets(csvfile, adminid, contentid, end, mongo, dryrun):
    click.secho('= params info =', fg='cyan')
    click.secho('csvfile: %s' % (csvfile), fg='green')
    click.secho('mongodb: %s' % (mongo), fg='green')
    now = datetime.utcnow()
    if csvfile and contentid and adminid and end:
        try:
            datetime.strptime(end, '%Y-%m-%dT%H:%M:%S')
        except ValueError as e:
            click.secho(str(e), fg='red')
            return -1
        count = 0
        except_users = list()
        slack = Slacker('xoxp-24065128659-73904001223-569430935267-9b2f294c10839df3b30241f2641f6a8c')
        mongo_client = MongoClient(host=mongo.split(':')[0], port=int(mongo.split(':')[1]))
        users = csv.DictReader(open(csvfile, 'r'))
        for u in users:
            if u['mobile_number'].startswith('010'):
                pass
            else:
                except_users.append(u)
                continue
            ticket_type = mongo_client['coconut']['ticket_type'].find_one({'name': u['ticket_type_name'], 'desc.value': u['ticket_type_desc']})
            if ticket_type:
                ticket_type_oid = ticket_type['_id']
            else:
                ticket_type_doc = {
                    'type': 'network',
                    'admin_oid': ObjectId(adminid),
                    'content_oid': ObjectId(contentid),
                    'name': u['ticket_type_name'].strip(),
                    'desc': {
                        'enabled': True,
                        'value': u['ticket_type_desc'].strip()
                    },
                    'fpfg': {
                        'now': 0,
                        'spread': None,
                        'limit': 1000
                    },
                    'price': 0,
                    'duplicated_registration': False,
                    'disabled_send': True,
                    'sales_date': {
                        'start': now,
                        'end': datetime.strptime(end, '%Y-%m-%dT%H:%M:%S') + timedelta(hours=-9)
                    },
                    'color': 'tkit-mint',
                    'enabled': True,
                    'created_at': now,
                    'updated_at': now
                }
                ticket_type_oid = mongo_client['coconut']['ticket_type'].insert(ticket_type_doc)
                if dryrun:
                    text = '<%s> / %s / %d원 / %d장 (스프레드 %s장)' % ('대용량엑셀파일 티켓 리스트 업로드 테스트', u['ticket_type_name'], 0, 1000, None)
                    slack_msg = [
                        {
                            'title': '[%s] 티켓생성' % '테스트',
                            'title_link': '%s://%s/ticket/type;content_oid=%s' % ('https', 'devhost.tkit.me', contentid),
                            'fallback': text,
                            'text': text,
                            'mrkdwn_in': ['text']
                        }
                    ]
                    slack.chat.post_message(channel='#notice', text=None, attachments=slack_msg, as_user=False)

            user = mongo_client['coconut']['user'].find_one({'mobile.country_code': '82', 'mobile.number': u['mobile_number'].strip(), 'enabled': True})
            if user:
                user_oid = user['_id']
            else:
                if u['gender'] == '남자' or u['gender'] == '남성':
                    gender = 'male'
                elif u['gender'] == '여자' or u['gender'] == '여성':
                    gender = 'female'
                else:
                    gender = 'female'
                user_oid = mongo_client['coconut']['user'].insert({
                    'name': u['name'].strip(),
                    'mobile': {
                        'country_code': '82',
                        'number': u['mobile_number'].strip()
                    },
                    'birthday': u['birthday'],
                    'gender': gender,
                    'terms': {
                        'policy': False,
                        'privacy': False
                    },
                    'enabled': True,
                    'created_at': now,
                    'updated_at': now
                })
            ticket_order_doc = {
                'type': 'network',
                'content_oid': ObjectId(contentid),
                'ticket_type_oid': ticket_type_oid,
                'admin_oid': ObjectId(adminid),
                'user_oid': user_oid,
                'qty': int(u['qty']),
                'enabled': True,
                'created_at': now,
                'updated_at': now,
                'receiver': {
                    'name': u['name'],
                    'mobile': {
                        'country_code': '82',
                        'number': u['mobile_number']
                    }
                }
            }
            ticket_order_oid = mongo_client['coconut']['ticket_order'].insert(ticket_order_doc)
            if dryrun:
                slack_msg = [
                    {
                        'title': '[%s] 티켓전송' % '테스트',
                        'title_link': '%s://%s/ticket/order;ticket_type_oid=%s' % ('https', 'devhost.tkit.me', ticket_type_oid),
                        'fallback': '[%s] 티켓전송 / <%s> / %s / %d원 / %d장 / %s 전달' % ('테스트', '대용량엑셀파일 티켓 리스트 업로드 테스트', u['ticket_type_name'], 0, int(u['qty']), u['name']),
                        'text': '<%s> / %s / %d원 / %d장 / %s 전달' % ('대용량엑셀파일 티켓 리스트 업로드 테스트', u['ticket_type_name'], 0, int(u['qty']), u['name']),
                        'mrkdwn_in': ['text']
                    }
                ]
                slack.chat.post_message(channel='#notice', text=None, attachments=slack_msg, as_user=False)

            for t in range(int(u['qty'])):
                ticket_doc = {
                    'type': 'network',
                    'content_oid': ObjectId(contentid),
                    'ticket_type_oid': ticket_type_oid,
                    'ticket_order_oid': ticket_order_oid,
                    'receive_user_oid': user_oid,
                    'status': 'send',
                    'price': 0,
                    'enabled': True,
                    'created_at': now,
                    'updated_at': now
                }
                ticket_oid = mongo_client['coconut']['ticket'].insert(ticket_doc)
            count = count + 1
        pprint('success count of user: %s' % count)
        pprint('except users: %s' % len(except_users))
        pprint(except_users)
    else:
        click.secho('check parameters <python import_v2.py list_tickets --help>', fg='red')


cli = click.CommandCollection(sources=[list_ticket])


if __name__ == '__main__':
    cli()
