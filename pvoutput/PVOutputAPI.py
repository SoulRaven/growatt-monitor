#  -*- coding: utf-8 -*-

import logging
from datetime import datetime
from time import sleep, time

import requests
from RoundBox.conf.project_settings import settings

logger = logging.getLogger(__name__)


# Local time with timezone
def localnow():
    return datetime.now(tz=settings.TIME_ZONE)


class PVOutputAPI:
    def __init__(self, api=None, system_id=None):
        """

        :param api:
        :param system_id:
        """

        if not any([api, system_id]):
            logger.error("You must set the API key and system_id parameters")

        self._API = api
        self._systemID = system_id
        self._wh_today_last = 0

    def add_status(self, payload, system_id=None):
        """Add live output data. Data should contain the parameters as described
        here: https://pvoutput.org/help.html#api-addstatus

        :param payload:
        :param system_id:
        :return:
        """
        sys_id = system_id if system_id is not None else self._systemID
        self.__call("https://pvoutput.org/service/r2/addstatus.jsp", payload, sys_id)

    def add_output(self, payload, system_id=None):
        """Add end of day output information. Data should be a dictionary with
        parameters as described here: https://pvoutput.org/help.html#api-addoutput

        :param payload:
        :param system_id:
        :return:
        """
        sys_id = system_id if system_id is not None else self._systemID
        self.__call("https://pvoutput.org/service/r2/addoutput.jsp", payload, sys_id)

    def __call(self, url, payload, system_id=None):
        headers = {
            'X-Pvoutput-Apikey': self._API,
            'X-Pvoutput-SystemId': system_id,
            'X-Rate-Limit': '1',
        }
        # Make tree attempts
        for i in range(1):
            try:
                r = requests.post(url, headers=headers, data=payload, timeout=10)
                if 'X-Rate-Limit-Reset' in r.headers:
                    reset = round(float(r.headers['X-Rate-Limit-Reset']) - time())
                    if int(r.headers['X-Rate-Limit-Remaining']) < 10:
                        logger.info(
                            "Only {} requests left, reset after {} seconds".format(
                                r.headers['X-Rate-Limit-Remaining'], reset
                            )
                        )
                if r.status_code == 403:
                    print("Forbidden: " + r.reason)
                else:
                    r.raise_for_status()
                    break
            except requests.exceptions.HTTPError as errh:
                logger.error("Http Error:", errh)
                # print(localnow().strftime('%Y-%m-%d %H:%M'), " Http Error:", errh)
            except requests.exceptions.ConnectionError as errc:
                logger.error("Error Connecting:", errc)
                # print(localnow().strftime('%Y-%m-%d %H:%M'), "Error Connecting:", errc)
            except requests.exceptions.Timeout as errt:
                logger.error("Timeout Error:", errt)
                # print(localnow().strftime('%Y-%m-%d %H:%M'), "Timeout Error:", errt)
            except requests.exceptions.RequestException as err:
                logger.error("OOps: Something Else", err)
                # print(localnow().strftime('%Y-%m-%d %H:%M'), "OOps: Something Else", err)

            sleep(5)
        else:
            logger.warning(f"Failed to call PVOutput API after {i} attempts.")
            # print(localnow().strftime('%Y-%m-%d %H:%M'),
            #      "Failed to call PVOutput API after {} attempts.".format(i))

    def send_status(
        self,
        date,
        energy_gen=None,
        power_gen=None,
        energy_imp=None,
        power_imp=None,
        temp=None,
        vdc=None,
        cumulative=False,
        vac=None,
        temp_inv=None,
        energy_life=None,
        comments=None,
        power_vdc=None,
        system_id=None,
    ) -> None:
        """

        :param date:
        :param energy_gen:
        :param power_gen:
        :param energy_imp:
        :param power_imp:
        :param temp:
        :param vdc:
        :param cumulative:
        :param vac:
        :param temp_inv:
        :param energy_life:
        :param comments:
        :param power_vdc:
        :param system_id:
        :return:
        """

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
