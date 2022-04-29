#  -*- coding: utf-8 -*-

from pprint import pprint
from RoundBox.dispatch import receiver
from RoundBox.conf.app_settings import app_settings

from growatt_web_api.signals import runtime_send
from growatt_web_api.growatt import growatt_runtime

from . import growatt


influxdb_url = getattr(app_settings, 'INFLUXDB_URL')
influxdb_token = getattr(app_settings, 'INFLUXDB_TOKEN')
influxdb_org = getattr(app_settings, 'INFLUXDB_ORG')
influxdb_gzip = getattr(app_settings, 'INFLUXDB_GZIP')
influxdb_timeout = getattr(app_settings, 'INFLUXDB_TIMEOUT')


@receiver(runtime_send, sender=growatt_runtime)
def receiver_growatt_runtime(sender, **kwargs):
    """

    :param sender:
    :param kwargs:
    :return:
    """

    entities = kwargs.get('entities')
    with growatt.GrowattInfluxDB(
        url=influxdb_url,
        token=influxdb_token,
        org=influxdb_org,
        gzip=influxdb_gzip,
        timeout=influxdb_timeout,
    ) as client:
        data = client.process_data(entities)
