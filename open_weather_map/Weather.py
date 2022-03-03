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

import logging
import re
from pyowm import OWM

log = logging.getLogger('growatt_logging')


class OpenWeatherMap:

    def __init__(self, api, lat, lon):
        self._API = api
        self._lat = float(lat)
        self._lon = float(lon)

        owm = OWM(self._API)
        self._owm_mgr = owm.weather_manager()

        self.temperature = 0.0
        self.cloud_pct = 0
        self.cmo_str = ''
        self.fresh = False

    def get(self):
        try:
            obs = self._owm_mgr.weather_at_coords(self._lat, self._lon)
            w = obs.weather
            status = w.detailed_status
            self.temperature = w.temperature('celsius')['temp']
            self.cloud_pct = w.clouds
            self.cmo_str = ('%s with cloud coverage of %s percent' % (status, self.cloud_pct))
            self.fresh = True
        except Exception as e:
            log.error('Getting weather: {}'.format(e))
            self.fresh = False
