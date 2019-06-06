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


@click.group()
def tmp7():
    pass

@tmp7.command()
@click.option('-m', '--mobile', default=None, help='mobile number only South Korea')
@click.option('-r', '--receive', default=None, help='receive user name')
@click.option('-s', '--send', default=None, help='send user name')
@click.option('-c', '--content', default=None, help='content name')
@click.option('-q', '--qty', default=None, help='quantity of ticket')
@click.option('-d', '--date', default=None, help='date of content')
@click.option('-p', '--place', default=None, help='place of content')
@click.option('-i', '--shortid', default=None, help='short id of content')
@click.confirmation_option(help='Are you sure to send message by kakaotalk?')
def tmp007(mobile, receive, send, content, qty, date, place, shortid):
    click.secho('= params info =', fg='cyan')
    click.secho('mobile: %s' % (mobile), fg='green')
    if mobile and receive and send and content and qty and date and place and shortid:
        TMPL_007 = '[TKIT 티켓]\n%s님 안녕하세요.\n%s님에게 요청하신 TKIT 티켓이 도착하였습니다.\n\n■ 공연제목 : %s\n■ 매수 : %s장\n■ 공연날짜 : %s\n■ 공연장소 : %s\n■ 밴딩수령장소 : %s\n\n수령하신 티켓은 TKIT에서 확인 가능합니다.\n로그인후 등록을 해주세요'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'x-waple-authorization': KEY
        }
        payload = {
            'callback': '15999642',
            'phone': mobile,
            'template_code': '007',
            'msg': TMPL_007 % (receive, send, content, qty, date, place, place),
            'btn_types': '웹링크',
            'btn_txts': 'TKIT확인하기',
            'btn_urls1': 'http://i.tkit.me/in/%s' % shortid
        }
        res = requests.post(APISTORE_KAKAO_URL, data=payload, headers=headers)
        pprint(res)
        pprint(res.json())
    else:
        click.secho('check parameters <python kakaotalk.py tmp007 --help>', fg='red')


@click.group()
def tmp7csv():
    pass

@tmp7csv.command()
@click.option('-c', '--csvfile', default=None, help='csv file')
@click.confirmation_option(help='Are you sure to send message by kakaotalk?')
def tmp007csv(csvfile):
    click.secho('= params info =', fg='cyan')
    click.secho('csv filename: %s' % (csvfile), fg='green')
    if csvfile:
        TMPL_007 = '[TKIT 티켓]\n%s님 안녕하세요.\n%s님에게 요청하신 TKIT 티켓이 도착하였습니다.\n\n■ 공연제목 : %s\n■ 매수 : %s장\n■ 공연날짜 : %s\n■ 공연장소 : %s\n■ 밴딩수령장소 : %s\n\n수령하신 티켓은 TKIT에서 확인 가능합니다.\n로그인후 등록을 해주세요'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'x-waple-authorization': KEY
        }
        users = csv.DictReader(open(csvfile, 'r'))
        for u in users:
            payload = {
                'callback': '15999642',
                'phone': u['MOBILE_NUMBER'],
                'template_code': '007',
                'msg': TMPL_007 % (u['RECEIVE_NAME'], u['SEND_NAME'], u['CONTENT'], u['QTY'], u['DATE'], u['PLACE'], u['BANDING_PLACE']),
                'btn_types': '웹링크',
                'btn_txts': 'TKIT확인하기',
                'btn_urls1': 'http://i.tkit.me/in/%s' % u['SHORT_OID']
            }
            res = requests.post(APISTORE_KAKAO_URL, data=payload, headers=headers)
            pprint(res)
            pprint(res.json())
    else:
        click.secho('check parameters <python kakaotalk.py tmp007csv --help>', fg='red')



@click.group()
def tmp5():
    pass

@tmp5.command()
@click.option('-m', '--mobile', default=None, help='mobile number only South Korea')
@click.option('-r', '--receive', default=None, help='receive user name')
@click.option('-c', '--content', default=None, help='content name')
@click.option('-d', '--date', default=None, help='date of content')
@click.option('-p', '--place', default=None, help='place of content')
@click.option('-l', '--link', default=None, help='url link')
@click.option('-i', '--shortid', default=None, help='short id of content')
@click.confirmation_option(help='Are you sure to send message by kakaotalk?')
def tmp005(mobile, receive, content, date, place, link, shortid):
    click.secho('= params info =', fg='cyan')
    click.secho('mobile: %s' % (mobile), fg='green')
    if mobile and receive and content and date and place and link and shortid:
        TMPL_005 = '%s님  내일은 등록하신초대권 %s공연 날입니다.\n\n\n장소: %s\n\n일시 : %s\n\n\n내 초대권 보기 %s\n\n\n \n\n* 주의 : 입장 전 본인 등록이 필요합니다.'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'x-waple-authorization': KEY
        }
        payload = {
            'callback': '15999642',
            'phone': mobile,
            'template_code': '005',
            'msg': TMPL_005 % (receive, content, place, date, link),
            'btn_types': '웹링크',
            'btn_txts': '내 초대권 보기',
            'btn_urls1': 'http://i.tkit.me/in/%s' % shortid
        }
        res = requests.post(APISTORE_KAKAO_URL, data=payload, headers=headers)
        pprint(res)
        pprint(res.json())
    else:
        click.secho('check parameters <python kakaotalk.py tmp005 --help>', fg='red')



@click.group()
def tmp5csv():
    pass

@tmp5csv.command()
@click.option('-c', '--csvfile', default=None, help='csv file')
@click.confirmation_option(help='Are you sure to send message by kakaotalk?')
def tmp005csv(csvfile):
    click.secho('= params info =', fg='cyan')
    click.secho('csv filename: %s' % (csvfile), fg='green')
    if csvfile:
        TMPL_005 = '%s님  내일은 등록하신초대권 %s공연 날입니다.\n\n\n장소: %s\n\n일시 : %s\n\n\n내 초대권 보기 %s\n\n\n \n\n* 주의 : 입장 전 본인 등록이 필요합니다.'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'x-waple-authorization': KEY
        }
        users = csv.DictReader(open(csvfile, 'r'))
        for u in users:
            payload = {
                'callback': '15999642',
                'phone': u['MOBILE_NUMBER'],
                'template_code': '005',
                'msg': TMPL_005 % (u['RECEIVE_NAME'], u['CONTENT'], u['PLACE'], u['DATE'], u['LINK']),
                'btn_types': '웹링크',
                'btn_txts': '내 초대권 보기',
                'btn_urls1': 'http://i.tkit.me/in/%s' % u['SHORT_OID']
            }
            res = requests.post(APISTORE_KAKAO_URL, data=payload, headers=headers)
            pprint(res)
            pprint(res.json())
    else:
        click.secho('check parameters <python kakaotalk.py tmp007csv --help>', fg='red')



cli = click.CommandCollection(sources=[tmp3, tmp3csv, tmp7, tmp7csv, tmp5, tmp5csv])


if __name__ == '__main__':
    cli()
