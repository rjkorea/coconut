# -*- coding: utf-8 -*-

import logging
from common.utils import Singleton
import requests


class KakaotalkService(Singleton):
    APISTORE_KAKAO_URL = 'http://api.apistore.co.kr/kko/1/msg/tkit'
    KEY = 'ODk4NC0xNTMzMDI0NzgwMTIyLWM0OGMyNGIxLWM3YzktNGNjMC04YzI0LWIxYzdjOTdjYzAyYw=='

    def __new__(cls, *args, **kwargs):
        _instance = super(KakaotalkService, cls).__new__(cls, *args)
        return _instance

    @classmethod
    def tmp003(cls, mobile, receive, send, content, qty, date, shortid):
        TMPL_003 = '[TKIT 티켓]\n%s님 안녕하세요.\n%s님에게 요청하신 TKIT 티켓이 도착하였습니다.\n\n■ 공연제목 : %s\n■ 매수 : %s장\n■ 공연날짜 : %s\n\n수령하신 티켓은 TKIT에서 확인 가능합니다.\n주의. 한정수량 티켓은 우선 등록자만 사용이 가능합니다.\n46시간 이후 등록 안된 티켓은 소멸 될 수 있습니다.\n'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'x-waple-authorization': cls.KEY
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
        res = requests.post(cls.APISTORE_KAKAO_URL, data=payload, headers=headers)
        logging.info(res)
        logging.info(res.json())

    @classmethod
    def tmp007(cls, mobile, receive, send, content, qty, date, place, band_place, shortid):
        TMPL_007 = '[TKIT 티켓]\n%s님 안녕하세요.\n%s님에게 요청하신 TKIT 티켓이 도착하였습니다.\n\n■ 공연제목 : %s\n■ 매수 : %s장\n■ 공연날짜 : %s\n■ 공연장소 : %s\n■ 밴딩수령장소 : %s\n\n수령하신 티켓은 TKIT에서 확인 가능합니다.\n로그인후 등록을 해주세요'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'x-waple-authorization': cls.KEY
        }
        payload = {
            'callback': '15999642',
            'phone': mobile,
            'template_code': '007',
            'msg': TMPL_007 % (receive, send, content, qty, date, place, band_place),
            'btn_types': '웹링크',
            'btn_txts': 'TKIT확인하기',
            'btn_urls1': 'http://i.tkit.me/in/%s' % shortid
        }
        res = requests.post(cls.APISTORE_KAKAO_URL, data=payload, headers=headers)
        logging.info(res)
        logging.info(res.json())

    @classmethod
    def tmp017(cls, mobile, receive, send, content, date, place, ticket):
        TMPL_017 = '[세상의 모든 즐거움 - 티킷]\n%s님 안녕하세요.\n%s님으로 부터 받은 TKIT이 취소되었습니다!\n\n\n■ 행사이름 : %s\n■ 행사일시 : %s\n■ 행사장소 : %s\n■ 티켓타입 : %s\n\n'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'x-waple-authorization': cls.KEY
        }
        payload = {
            'callback': '15999642',
            'phone': mobile,
            'template_code': '017',
            'msg': TMPL_017 % (receive, send, content, date, place, ticket)
        }
        res = requests.post(cls.APISTORE_KAKAO_URL, data=payload, headers=headers)
        logging.info(res)
        logging.info(res.json())

    @classmethod
    def tmp032(cls, mobile, receive, send, content, ticket, qty, others,shortid):
        TMPL_032 = '[TKIT 티킷]\n <%s>님 안녕하세요.\n <%s>님으로 부터\n TKIT이 도착했습니다 :)\n\n■ %s\n   - %s <%s장>\n     %s \n\n수령하신 TKIT을 확인 하시려면\n아래 버튼을 눌러 로그인 해주세요.'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'x-waple-authorization': cls.KEY
        }
        payload = {
            'callback': '15999642',
            'phone': mobile,
            'template_code': '032',
            'msg': TMPL_032 % (receive, send, content, ticket, qty, others),
            'btn_types': '웹링크',
            'btn_txts': 'TKIT 확인하기',
            'btn_urls1': 'http://i.tkit.me/in/%s' % shortid
        }
        res = requests.post(cls.APISTORE_KAKAO_URL, data=payload, headers=headers)
        logging.info(res)
        logging.info(res.json())
