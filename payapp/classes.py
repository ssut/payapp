# coding=utf-8
from collections import namedtuple

__all__ = ['Struct', 'PayAppInternalResult', 'PayType', 'PayState', ]


class Struct(object):
    def __init__(self, **entries):
        self.__dict__.update(entries)

    def __repr__(self):
        return str(self.__dict__)

    def __contains__(self, item):
        return item in self.__dict__


class PayAppInternalResult(namedtuple('PayAppInternalResult',
                           ['success', 'error', 'content'])):
    pass


class PayType(object):
    TYPES = (None, u'신용카드', u'휴대전화', u'해외결제', u'대면결제', None,
             u'계좌이체', u'가상계좌', None, u'문화상품권')

    def __init__(self, type_id):
        if type(type_id) is not int:
            type_id = int(type_id)
        self.type_id = type_id

    def __int__(self):
        return self.type_id

    def __str__(self):
        return PayType.TYPES[self.type_id]

    def __repr__(self):
        return str(self.type_id)


class PayState(object):
    STATES = (
        ([1], u'요청', 'req'), ([4], u'결제완료', 'approved'), ([8, 16, 32], u'요청취소', 'cancel'),
        ([9, 64], u'승인취소', 'cancel-approval'), ([10], u'결제대기', 'waiting')
    )

    def __init__(self, state_id):
        if type(state_id) is not int:
            state_id = int(state_id)
        self.state_id = state_id
        self.state_name = next(state[1] for state in PayState.STATES if state_id in state[0])
        self.stat = next(state[2] for state in PayState.STATES if state_id in state[0])

    @property
    def code(self):
        return self.stat

    def __int__(self):
        return self.state_id

    def __str__(self):
        return self.state_name

    def __repr__(self):
        return str(self.state_id)
