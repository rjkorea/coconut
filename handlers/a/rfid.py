# -*- coding: utf-8 -*-

import logging

from bson import ObjectId
from datetime import datetime

import mysql.connector
from mysql.connector import Error

from tornado.web import HTTPError

from common.decorators import admin_auth_async

from models.ticket import TicketModel

from handlers.base import JsonHandler

from services.mysql import MySQLService

import settings


class RfidUmfKoreaSyncHandler(JsonHandler):
    @admin_auth_async
    async def put(self, *args, **kwargs):
        uid = self.json_decoded_body.get('uid', None)
        if not uid or len(uid)==0:
            raise HTTPError(400, self.set_error(1, 'invalid uid'))
        user = self.json_decoded_body.get('user', None)
        if not user or not isinstance(user, dict):
            raise HTTPError(400, self.set_error(1, 'invalid user'))
        ticket = self.json_decoded_body.get('ticket', None)
        if not ticket or not isinstance(ticket, dict):
            raise HTTPError(400, self.set_error(1, 'invalid ticket'))
        conn = None
        try:
            conn = MySQLService().client.get_connection()
            if conn.is_connected():
                db_info = conn.get_server_info()
                logging.info('Connected to MySQL % s' % db_info)
                cursor = conn.cursor(prepared=True)
                bands_select_query = '''SELECT * FROM bands WHERE uid = %s'''
                select_params = (uid,)
                logging.info(dict(uid=uid, type='request_mysql', timestamp=datetime.utcnow()))
                cursor.execute(bands_select_query, select_params)
                record = cursor.fetchone()
                if record:
                    band = dict(
                        id=record[0],
                        band_code=record[1],
                        uid=record[2],
                        status=record[3],
                        updated_at=record[4]
                    )
                    if band['status'] == '0':
                        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        bands_update_query = '''UPDATE bands set status = %s, updated_at = %s WHERE id = %s'''
                        update_params = ('1', now, band['id'])
                        cursor.execute(bands_update_query, update_params)
                        conn.commit()
                        gate_dbs_insert_query = '''INSERT INTO gate_dbs (name, email, country, phone, birth, gender, type, photo_loc, real_loc, photo_stat, band_code, uid, status, passtime_fri, passtime_sat, passtime_sun, created_at, updated_at, memo) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
                        insert_params = (
                            user['name'],
                            'tkit@tkit.me',
                            self.get_country(user['mobile']['country_code']),
                            user['mobile']['number'],
                            self.get_birthday(user['birthday']),
                            self.get_gender(user['gender']),
                            'GA',
                            '',
                            None,
                            '0',
                            band['band_code'],
                            band['uid'],
                            '0',
                            None,
                            None,
                            None,
                            now,
                            now,
                            '초대-%s' % (ticket['name'])
                        )
                        cursor.execute(gate_dbs_insert_query, insert_params)
                        conn.commit()
                        logging.info(dict(uid=uid, type='response_mysql', timestamp=datetime.utcnow()))
                        query = {
                            '_id': ObjectId(ticket['_id'])
                        }
                        set_doc = {
                            '$set': {
                                'status': TicketModel.Status.use.name,
                                'updated_at': datetime.utcnow()
                            }
                        }
                        await TicketModel.update(query, set_doc, False, False)
                    else:
                        raise HTTPError(400, self.set_error(3, 'can\'t available band'))
                    self.response['data'] = band
                    self.write_json()
                else:
                    raise HTTPError(400, self.set_error(2, 'no exist uid'))
        except Error as e:
            conn.rollback()
            raise HTTPError(500, self.set_error(1, str(e)))
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()
                logging.info('MySQL connection is closed')

    def get_gender(self, gender):
        if gender == 'male':
            return 0
        else:
            return 1

    def get_birthday(self, birthday):
        if len(birthday) == 4:
            return '%s-01-01' % (birthday)
        elif len(birthday) == 8:
            return '%s-%s-%s' % (birthday[:4], birthday[4:6], birthday[6:8])
        else:
            return '1990-01-01'

    def get_country(self, code):
        if code == '82':
            return 'Korea, \nRepublic Of'
        else:
            return 'Foreigner'

    async def options(self, *args, **kwargs):
        self.response['message'] = 'OK'
        self.write_json()
