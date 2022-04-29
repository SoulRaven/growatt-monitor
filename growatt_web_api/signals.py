#  -*- coding: utf-8 -*-

from RoundBox.dispatch import Signal, receiver

pre_login = Signal()
post_login = Signal()

pre_logout = Signal()
post_logout = Signal()

runtime_send = Signal()


# @receiver([init_proxy], sender=Proxy)
# def login_events(sender, data, **kwargs):
#     print('LOGIN EVENTS SIGNALS')
#     print(sender)
#     print(data)
