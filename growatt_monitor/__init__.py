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

import os

from growatt_monitor.conf import settings
from growatt_monitor.utils.log import configure_logging
from growatt_monitor.utils import version
from growatt_monitor.core.exceptions import WrongPyVersion

os.environ.setdefault('GROWATT_MONITOR_SETTINGS_MODULE', 'growatt_monitor.settings')
configure_logging(settings.LOGGING_CONFIG, settings.LOGGING)

if not version.PY36:
    raise WrongPyVersion("🐍 This script requires Python 3.6+")
