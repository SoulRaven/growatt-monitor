#  -*- coding: utf-8 -*-


import logging

from roundBox.conf.global_settings import settings
from roundBox.core.web.GrowattWeb import GrowattWeb
from roundBox.core.web.signals import post_login
from roundBox.dispatch import receiver


@receiver([post_login], sender=GrowattWeb)
def login_events(sender, data, **kwargs):
    print('LOGIN EVENTS SIGNALS')
    print(sender)
    print(data)
