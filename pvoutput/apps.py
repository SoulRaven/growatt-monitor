#  -*- coding: utf-8 -*-

import os
import time


from RoundBox.apps import AppConfig
from RoundBox.conf.project_settings import settings
from RoundBox.conf.app_settings import app_settings


class PVOutputConfig(AppConfig):
    name = 'pvoutput'
    verbose_name = 'PVOutput'

    def ready(self):
        """

        :return:
        """
        import pvoutput.signals  # noqa

        # logger.info(f'Start {self.verbose_name}[{os.getpid()}]')
        #
        # schedule_delay_settings = getattr(self.args_parse, 'schedule_delay_tasks', app_settings.SCHEDULE_DELAY_TASKS)
        # schedule.every(schedule_delay_settings).seconds.do(lambda: GrowattWeb.growatt_process_data())
        #
        # try:
        #     while True:
        #         schedule.run_pending()
        #         time.sleep(1)
        # except:
        #     schedule.clear()
        #     logger.exception('Growatt Web API fail with exception')
