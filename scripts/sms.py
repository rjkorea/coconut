# -*- coding: utf-8 -*-

from datetime import datetime
from pprint import pprint

import click
import requests
import csv


APISTORE_LMS_URL = 'http://api.apistore.co.kr/ppurio/1/message/lms/tkit'
KEY = 'ODk4NC0xNTMzMDI0NzgwMTIyLWM0OGMyNGIxLWM3YzktNGNjMC04YzI0LWIxYzdjOTdjYzAyYw=='


@click.group()
def lms():
    pass

@lms.command()
@click.option('-p', '--phone', default=None, help='phone number only South Korea')
@click.option('-s', '--subject', default=None, help='lms of subject')
@click.option('-m', '--message', default=None, help='receive user name')
@click.confirmation_option(help='Are you sure to send message by lms?')
def lmss(phone, subject, message):
    click.secho('= params info =', fg='cyan')
    click.secho('mobile: %s' % (phone), fg='green')
    if phone and subject and message:
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'x-waple-authorization': KEY
        }
        payload = {
            'send_phone': '15999642',
            'dest_phone': phone,
            'subject': subject,
            'msg_body': message
        }
        res = requests.post(APISTORE_LMS_URL, data=payload, headers=headers)
        pprint(res)
        pprint(res.json())
    else:
        click.secho('check parameters <python sms.py lmss --help>', fg='red')


@click.group()
def lmscsv():
    pass

@lmscsv.command()
@click.option('-c', '--csvfile', default=None, help='csv file')
@click.confirmation_option(help='Are you sure to send message by lms?')
def lmscsvs(csvfile):
    click.secho('= params info =', fg='cyan')
    click.secho('csv filename: %s' % (csvfile), fg='green')
    if csvfile:
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'x-waple-authorization': KEY
        }
        users = csv.DictReader(open(csvfile, 'r'))
        for u in users:
            payload = {
                'send_phone': '15999642',
                'dest_phone': u['MOBILE_NUMBER'],
                'subject': u['SUBJECT'],
                'msg_body': u['MESSAGE']
            }
            res = requests.post(APISTORE_LMS_URL, data=payload, headers=headers)
            pprint(res)
            pprint(res.json())
    else:
        click.secho('check parameters <python sms.py lmscsvs --help>', fg='red')


cli = click.CommandCollection(sources=[lms, lmscsv])


if __name__ == '__main__':
    cli()
