#  -*- coding: utf-8 -*-

from RoundBox.dispatch import receiver

from growatt_web_api.signals import runtime_send
from growatt_web_api.growatt import growatt_runtime


@receiver(runtime_send, sender=growatt_runtime)
def receiver_growatt_runtime(sender, **kwargs):
    """

    :param sender:
    :param kwargs:
    :return:
    """

    pass
