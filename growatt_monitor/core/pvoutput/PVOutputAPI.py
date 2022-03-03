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
import requests
from time import sleep, time
from datetime import datetime

from growatt_monitor.conf import settings

log = logging.getLogger('growatt_logging')


# Local time with timezone
def localnow():
    return datetime.now(tz=settings.TIME_ZONE)


class PVOutputAPI:

    def __init__(self, api=None, system_id=None):
        self._API = api or getattr(settings, 'PV_OUTPUT_KEY', None)
        self._systemID = system_id or getattr(settings, 'PV_OUTPUT_SYSTEM_ID', None)
        self._wh_today_last = 0

    def add_status(self, payload, system_id=None):
        """Add live output data. Data should contain the parameters as described
        here: https://pvoutput.org/help.html#api-addstatus .
        """
        sys_id = system_id if system_id is not None else self._systemID
        self.__call("https://pvoutput.org/service/r2/addstatus.jsp", payload, sys_id)

    def add_output(self, payload, system_id=None):
        """Add end of day output information. Data should be a dictionary with
        parameters as described here: https://pvoutput.org/help.html#api-addoutput .
        """
        sys_id = system_id if system_id is not None else self._systemID
        self.__call("https://pvoutput.org/service/r2/addoutput.jsp", payload, sys_id)

    def __call(self, url, payload, system_id=None):
        headers = {
            'X-Pvoutput-Apikey': self._API,
            'X-Pvoutput-SystemId': system_id,
            'X-Rate-Limit': '1'
        }
        # Make tree attempts
        for i in range(1):
            try:
                r = requests.post(url, headers=headers, data=payload, timeout=10)
                if 'X-Rate-Limit-Reset' in r.headers:
                    reset = round(float(r.headers['X-Rate-Limit-Reset']) - time())
                    if int(r.headers['X-Rate-Limit-Remaining']) < 10:
                        log.info("Only {} requests left, reset after {} seconds".format(
                            r.headers['X-Rate-Limit-Remaining'],
                            reset))
                if r.status_code == 403:
                    print("Forbidden: " + r.reason)
                else:
                    r.raise_for_status()
                    break
            except requests.exceptions.HTTPError as errh:
                log.error("Http Error:", errh)
                # print(localnow().strftime('%Y-%m-%d %H:%M'), " Http Error:", errh)
            except requests.exceptions.ConnectionError as errc:
                log.error("Error Connecting:", errc)
                # print(localnow().strftime('%Y-%m-%d %H:%M'), "Error Connecting:", errc)
            except requests.exceptions.Timeout as errt:
                log.error("Timeout Error:", errt)
                # print(localnow().strftime('%Y-%m-%d %H:%M'), "Timeout Error:", errt)
            except requests.exceptions.RequestException as err:
                log.error("OOps: Something Else", err)
                # print(localnow().strftime('%Y-%m-%d %H:%M'), "OOps: Something Else", err)

            sleep(5)
        else:
            log.warning("Failed to call PVOutput API after {} attempts.".format(i))
            # print(localnow().strftime('%Y-%m-%d %H:%M'),
            #      "Failed to call PVOutput API after {} attempts.".format(i))

    def send_status(self, date, energy_gen=None, power_gen=None, energy_imp=None,
                    power_imp=None, temp=None, vdc=None, cumulative=False, vac=None,
                    temp_inv=None, energy_life=None, comments=None, power_vdc=None,
                    system_id=None):
        # format status payload
        payload = {
            'd': date.strftime('%Y%m%d'),
            't': date.strftime('%H:%M'),
        }

        # Only report total energy if it has changed since last upload
        # this trick avoids avg power to zero with inverter that reports
        # generation in 100 watts increments (Growatt and Canadian solar)
        if (energy_gen is not None) and (self._wh_today_last != energy_gen):
            self._wh_today_last = int(energy_gen)
            payload['v1'] = int(energy_gen)

        if power_gen is not None:
            payload['v2'] = float(power_gen)
        if energy_imp is not None:
            payload['v3'] = int(energy_imp)
        if power_imp is not None:
            payload['v4'] = float(power_imp)
        if temp is not None:
            payload['v5'] = float(temp)
        if vdc is not None:
            payload['v6'] = float(vdc)
        if cumulative is True:
            payload['c1'] = 1
        else:
            payload['c1'] = 0
        if vac is not None:
            payload['v8'] = float(vac)
        if temp_inv is not None:
            payload['v9'] = float(temp_inv)
        if energy_life is not None:
            payload['v10'] = int(energy_life)
        if comments is not None:
            payload['m1'] = str(comments)[:30]
        # calculate efficiency
        if (power_vdc is not None) and (power_vdc > 0) and (power_gen is not None):
            payload['v12'] = float(power_gen) / float(power_vdc)

        # Send status
        self.add_status(payload, system_id)
