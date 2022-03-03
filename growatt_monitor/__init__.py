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

import multiprocessing
import os

from growatt_monitor.utils.version import get_version
from growatt_monitor.utils.utils import check_dependency


VERSION = (1, 0, 0, "alpha", 0)

__version__ = get_version(VERSION)

os.environ.setdefault('GROWATT_MONITOR_SETTINGS_MODULE', 'settings')

# before any action, default operation is to check if any of the requirements packages are installed.
check_dependency()


def setup():
    """

    :return:
    """

    from growatt_monitor.apps import apps
    from growatt_monitor.conf import settings
    from growatt_monitor.utils.logs.loguru import Logger

    _logger = Logger(level='DEBUG' if settings.DEBUG else 'INFO')

    apps.populate(settings.INSTALLED_APPS, call_ready=False)

    if apps.ready:
        from multiprocessing import (Process, Pool, Queue, Lock, RLock, cpu_count)

        queue = Queue()
        rlock = RLock()

        all_apps = apps.get_app_configs()
        jobs = []

        for application in all_apps:
            p = Process(name=application.verbose_name, target=application.ready, args=(queue, rlock))
            p.daemon = False
            jobs.append(p)

        for job in jobs:
            job.start()
