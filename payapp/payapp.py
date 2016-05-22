# coding=utf-8
from datetime import datetime
try:
    from urllib.parse import parse_qsl
except ImportError:
    from urlparse import parse_qsl
import json

import requests

from .classes import Struct
from .classes import PayAppInternalResult, PayState, PayType

__all__ = ['PayApp', ]

CMD_LIST = ('payrequest', 'paycancel', 'paycancelreq', )
REST_URL = 'http://api.payapp.kr/oapi/apiLoad.html'


class PayApp(object):
    """Payapp API"""

    TEST_ID = 'payapptest'
    TEST_KEY = 'ALSL4bhw2kPlZ+NeonwmJ+1DPJnCCRVaOgT+oqg6zaM='
    TEST_VALUE = 'ALSL4bhw2kPlZ+NeonwmJ7lHBlJsugxqHSmEy6b48Xk='

    def __init__(self, user_id, link_key, link_value):
        self.user_id = user_id
        self.link_key = link_key
        self.link_value = link_value

    def _post(self, cmd, data={}):
        assert cmd in CMD_LIST
        assert self.user_id

        data.update({
            'cmd': cmd,
            'userid': self.user_id,
        })
        resp = requests.post(REST_URL, data=data)
        success = False
        error = None
        content = {}
        if resp.status_code == 200:
            data = dict(parse_qsl(resp.text))
            if data['state'] == '1':
                success = True
            elif 'errorMessage' in data:
                error = data['errorMessage']
            content = Struct(**{k: v for k, v in data.items() if k not in ('state', 'errorMessage')})
        result = PayAppInternalResult(success=success, error=error, content=content)

        return result

    def verify_callback(self, params):
        """올바른 콜백 데이터인지 확인합니다.

        :param params: `dict` 또는 쿼리 스트링 `str`, POST 데이터
        """
        if type(params) is str:
            params = Struct(**dict(parse_qsl(params)))
        elif type(params) is dict:
            params = Struct(**params)

        valid = True
        try:
            assert self.user_id == params.userid, u'판매자 회원 아이디가 일치하지 않습니다.'
            assert self.link_key == params.linkkey, u'연동 KEY가 일치하지 않습니다.'
            assert self.link_value == params.linkval, u''
        except (AssertionError, AttributeError) as e:
            valid = False
            print(e)

        return valid

    def parse_callback(self, params):
        """콜백 데이터를 사용히기 쉬운 형태로 파싱합니다.
        파싱된 정보는 반드시 검증을 거쳐야 합니다. (name, price, contact)

        :param params: `dict` 또는 쿼리 스트링 `str`, POST 데이터
        """
        if type(params) is str:
            params = Struct(**dict(parse_qsl(params)))
        elif type(params) is dict:
            params = Struct(**params)

        assert self.user_id == params.userid, u'판매자 회원 아이디가 일치하지 않습니다.'
        assert self.link_key == params.linkkey, u'연동 KEY가 일치하지 않습니다.'
        assert self.link_value == params.linkval, u''

        reqdate = datetime.strptime(params.reqdate, '%Y-%m-%d %H:%M:%S')
        paydate = None
        if params.pay_date != '':
            paydate = datetime.strptime(params.pay_date, '%Y-%m-%d %H:%M:%S')

        paystate = PayState(params.pay_state)
        paytype = None
        if paystate.code not in ('cancel') and len(params.pay_type) > 0:
            paytype = PayType(params.pay_type)

        restructed = {
            'name': params.goodname,
            'price': int(params.price),
            'contact': params.recvphone,
            'memo': params.memo,
            'request_date': reqdate,
            'user_memo': params.pay_memo,
            'user_addr': params.pay_addr,
            'pay_date': paydate,
            'pay_type': paytype,
            'pay_state': paystate,
            'var1': params.var1,
            'var2': params.var2,
            'identifier': params.mul_no,
            'url': params.payurl,
            'currency': params.currency,
        }

        # 신용카드 거래일 경우
        if paytype is not None and int(paytype) == 1:
            restructed.update({
                'pay_check_url': params.csturl,
                'pay_card_name': params.card_name,
            })
        # 가상계좌 거래일 경우
        elif 'vbank' in params and len(params.vbank) > 0:
            restructed.update({
                'pay_vbank': params.vbank,
                'pay_vbank_account': params.vbankno,
            })

        return Struct(**restructed)

    def pay_request(self, name, price, contact, callback, returns, use_sms=True,
                    paytype='card,rbank', memo='', var1='', var2=''):
        """결제를 요청합니다.

        :param name: 상품명
        :param price: 결제요청 금액
        :param contact: (recvphone) 수신 휴대폰번호
        :param callback: (feedbackurl) 결제 완료 피드백 URL
        :param returns: (returnurl) 결제 완료 후 이동할 URL
        :param use_sms: (smsuse) SMS 결제 사용여부
        :param paytype: (openpaytype) 결제수단
        :param memo: 메모
        :param var1: 임의 사용 변수 1
        :param var2: 임의 사용 변수 2
        """
        data = {
            'goodname': name,
            'price': price,
            'recvphone': contact,
            'memo': memo,
            'feedbackurl': callback,
            'var1': var1,
            'var2': var2,
            'returnurl': returns,
            'openpaytype': paytype,
        }
        if not use_sms:
            data['smsuse'] = 'n'
        result = self._post('payrequest', data=data)
        data = {
            'success': result.success,
            'error': result.error,
        }
        if result.success:
            data['identifier'] = result.content.mul_no
            data['url'] = result.content.payurl

        return Struct(**data)

    def pay_cancel(self, identifier, memo='', ready=False):
        """결제승인 후 5일이 지나지 않았거나, 정산이 완료되지 않은 경우 결제를 즉시 취소합니다.

        :param identifier: 결제요청번호
        :param memo: 결제요청취소 메모
        :param mode: 취소 모드, 'ready'인 경우 실제 취소는 이루어지지 않고 결제요청 상태만 취소됩니다.
        """
        data = {
            'linkkey': self.link_key,
            'mul_no': identifier,
        }
        if len(memo) > 0:
            data['cancelmemo'] = memo
        if ready:
            data['cancelmode'] = True
        result = self._post('paycancel', data=data)
        data = {
            'success': result.success,
            'error': result.error,
        }

        return Struct(**data)

    def pay_cancel_request(self, identifier, memo):
        """결제승인 후 5일이 지났거나, 정산이 이미 완료된 경우 결제 취소 요청을 보냅니다.

        :param identifier: 결제요청번호
        :param memo: 결제요청취소 메모
        """
        data = {
            'linkkey': self.link_key,
            'mul_no': identifier,
            'cancelmemo': memo,
        }
        result = self._post('paycancelreq', data=data)
        data = {
            'success': result.success,
            'error': result.error,
        }

        return Struct(**data)
