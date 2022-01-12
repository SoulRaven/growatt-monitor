#  -*- coding: utf-8 -*-
#
#              Copyright (C) 2018-<copyright_year> ProGeek
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

import os
import sys
import time
import logging

from datetime import datetime

from growatt_monitor.conf import settings
from growatt_monitor.utils.log import configure_logging
from growatt_monitor.utils.utils import load_arguments

from growattServer import Timespan

from growatt_monitor.core.GrowattWeb import GrowattWeb

log = logging.getLogger('growatt_logging')


if __name__ == '__main__':
    log.info("Start the Growatt Monitor script")
    args = load_arguments()
    try:
        with GrowattWeb(**vars(args)) as api:
            data = api.login()
            plant_info = api.mix_info()
    except KeyboardInterrupt:
        log.warning("Growatt Monitor script interrupted")
        sys.exit(1)
