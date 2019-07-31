# -*- coding: utf-8 -*-

import logging
from common.utils import Singleton
import requests


class LmsService(Singleton):
    APISTORE_LMS_URL = 'http://api.apistore.co.kr/ppurio/1/message/lms/tkit'
    KEY = 'ODk4NC0xNTMzMDI0NzgwMTIyLWM0OGMyNGIxLWM3YzktNGNjMC04YzI0LWIxYzdjOTdjYzAyYw=='

    def __new__(cls, *args, **kwargs):
        _instance = super(LmsService, cls).__new__(cls, *args)
        return _instance

    @classmethod
    def send(cls, phone, subject, message):
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'x-waple-authorization': cls.KEY
        }
        payload = {
            'send_phone': '15999642',
            'dest_phone': phone,
            'subject': subject,
            'msg_body': message
        }
        res = requests.post(cls.APISTORE_LMS_URL, data=payload, headers=headers)
        logging.info(res)
        logging.info(res.json())
        return res.json()
