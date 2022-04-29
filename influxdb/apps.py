#  -*- coding: utf-8 -*-

import os
import time


from RoundBox.apps import AppConfig
from RoundBox.conf.project_settings import settings
from RoundBox.conf.app_settings import app_settings


class GrowattInfluxdbClientConfig(AppConfig):
    name = 'influxdb'
    verbose_name = 'Growatt Influxdb client'

    def ready(self):
        import influxdb.signals  # noqa
