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

import multiprocessing

from loguru import logger

from growatt_monitor.apps import AppConfig
from .Proxy import Proxy


class GrowattProxyConfig(AppConfig):
    name = "growatt_proxy"
    verbose_name = 'Growatt Proxy Server'

    def ready(self, queue, rlock):
        import growatt_proxy.signals  # noqa

        logger.info('Start the Growatt Proxy server')
        current_process = multiprocessing.current_process()
        logger.info(f'Growatt Proxy server process name {current_process.name}[{current_process.pid}]')

        proxy = Proxy()
        proxy.main()
