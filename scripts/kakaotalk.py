# -*- coding: utf-8 -*-

from datetime import datetime
from pprint import pprint

import click
import requests
import csv


APISTORE_KAKAO_URL = 'http://api.apistore.co.kr/kko/1/msg/tkit'
KEY = 'ODk4NC0xNTMzMDI0NzgwMTIyLWM0OGMyNGIxLWM3YzktNGNjMC04YzI0LWIxYzdjOTdjYzAyYw=='


@click.group()
def tmp3():
    pass

@tmp3.command()
@click.option('-m', '--mobile', default=None, help='mobile number only South Korea')
@click.option('-r', '--receive', default=None, help='receive user name')
@click.option('-s', '--send', default=None, help='send user name')
@click.option('-c', '--content', default=None, help='content name')
@click.option('-q', '--qty', default=None, help='quantity of ticket')
@click.option('-d', '--date', default=None, help='date of content')
@click.option('-i', '--shortid', default=None, help='short id of content')
@click.confirmation_option(help='Are you sure to send message by kakaotalk?')
def tmp003(mobile, receive, send, content, qty, date, shortid):
    click.secho('= params info =', fg='cyan')
    click.secho('mobile: %s' % (mobile), fg='green')
    if mobile and receive and send and content and qty and date and shortid:
        TMPL_003 = '[TKIT 티켓]\n%s님 안녕하세요.\n%s님에게 요청하신 TKIT 티켓이 도착하였습니다.\n\n■ 공연제목 : %s\n■ 매수 : %s장\n■ 공연날짜 : %s\n\n수령하신 티켓은 TKIT에서 확인 가능합니다.\n주의. 한정수량 티켓은 우선 등록자만 사용이 가능합니다.\n46시간 이후 등록 안된 티켓은 소멸 될 수 있습니다.\n'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'x-waple-authorization': KEY
        }
        payload = {
            'callback': '15999642',
            'phone': mobile,
            'template_code': '003',
            'msg': TMPL_003 % (receive, send, content, qty, date),
            'btn_types': '웹링크',
            'btn_txts': '초대장확인하기',
            'btn_urls1': 'http://i.tkit.me/in/%s' % shortid
        }
        res = requests.post(APISTORE_KAKAO_URL, data=payload, headers=headers)
        pprint(res)
        pprint(res.json())
    else:
        click.secho('check parameters <python kakaotalk.py tmp003 --help>', fg='red')


@click.group()
def tmp3csv():
    pass

@tmp3csv.command()
@click.option('-c', '--csvfile', default=None, help='csv file')
@click.confirmation_option(help='Are you sure to send message by kakaotalk?')
def tmp003csv(csvfile):
    click.secho('= params info =', fg='cyan')
    click.secho('csv filename: %s' % (csvfile), fg='green')
    if csvfile:
        TMPL_003 = '[TKIT 티켓]\n%s님 안녕하세요.\n%s님에게 요청하신 TKIT 티켓이 도착하였습니다.\n\n■ 공연제목 : %s\n■ 매수 : %s장\n■ 공연날짜 : %s\n\n수령하신 티켓은 TKIT에서 확인 가능합니다.\n주의. 한정수량 티켓은 우선 등록자만 사용이 가능합니다.\n46시간 이후 등록 안된 티켓은 소멸 될 수 있습니다.\n'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'x-waple-authorization': KEY
        }
        users = csv.DictReader(open(csvfile, 'r'))
        for u in users:
            payload = {
                'callback': '15999642',
                'phone': u['MOBILE_NUMBER'],
                'template_code': '003',
                'msg': TMPL_003 % (u['RECEIVE_NAME'], u['SEND_NAME'], u['CONTENT'], u['QTY'], u['DATE']),
                'btn_types': '웹링크',
                'btn_txts': '초대장확인하기',
                'btn_urls1': 'http://i.tkit.me/in/%s' % u['SHORT_OID']
            }
            res = requests.post(APISTORE_KAKAO_URL, data=payload, headers=headers)
            pprint(res)
            pprint(res.json())
    else:
        click.secho('check parameters <python kakaotalk.py tmp003csv --help>', fg='red')


cli = click.CommandCollection(sources=[tmp3, tmp3csv])


if __name__ == '__main__':
    cli()
