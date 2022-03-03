#  -*- coding: utf-8 -*-

#  -*- coding: utf-8 -*-
#
#  Copyright (C) 2020-2022 ProGeek
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

#
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

import time
import multiprocessing

import schedule

from loguru import logger


from growatt_monitor.apps import AppConfig
from growatt_monitor.conf import settings

from .GrowattWeb import GrowattWeb


class GrowattWebApiConfig(AppConfig):
    name = 'growatt_web_api'
    verbose_name = 'Growatt Web Api'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.current_process = multiprocessing.current_process()

    def ready(self, queue, rlock):
        import growatt_web_api.signals  # noqa

        logger.info(
            f'Start the Growatt Web API thread {self.current_process.name}[{self.current_process.pid}]')

        schedule_delay_settings = getattr(self.args_parse, 'schedule_delay_tasks', settings.SCHEDULE_DELAY_TASKS)
        schedule.every(schedule_delay_settings).seconds.do(lambda: GrowattWeb.growatt_process_data())

        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except:
            schedule.clear()
            logger.exception('Growatt Web API fail with exception')
