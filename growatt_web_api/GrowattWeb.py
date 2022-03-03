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

import datetime
import json

from loguru import logger

from growatt_monitor.apps import apps
from growatt_monitor.conf import settings
from growatt_monitor.core.exceptions import ImproperlyConfigured

from growattServer import GrowattApi, hash_password, Timespan

from .signals import pre_login, post_login, pre_logout, post_logout


class GrowattWeb(GrowattApi):
    """

    """

    def __init__(
            self,
            username: str = None,
            password: str = None,
            is_password_hashed: bool = False,
            *args,
            **kwargs,
    ):
        super(GrowattWeb, self).__init__()
        self.logged_in = False

        self.username = username or kwargs.get(
            'username', getattr(settings, 'GROWATT_USERNAME', None)
        )
        self.password = password or kwargs.get(
            'password', getattr(settings, 'GROWATT_PASSWORD', None)
        )

        if any(x is None for x in [self.username, self.password]):
            raise ImproperlyConfigured(
                "Username or password are not defined in main script arguments"
            )

        self.is_password_hashed = is_password_hashed

        # setup endpoint
        self.server_url = getattr(settings, 'GROWATT_ENDPOINT_WEB_API')

        self.apps_config = apps.get_app_config('growatt_web_api')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.logged_in:
            self.logout()

    @classmethod
    def growatt_process_data(cls) -> dict:
        args_parse = cls().apps_config.args_parse

        output_data = {}
        print('Growatt process data called')
        with GrowattWeb(username=getattr(args_parse, 'username', settings.GROWATT_USERNAME),
                        password=getattr(args_parse, 'password', settings.GROWATT_PASSWORD)) as api:

            login_data = api.login()
            print(login_data)
            if login_data.get('success', False):

                user_id = login_data.get('userId')
                plant_id = login_data.get('data')[0]['plantId']

                plant_list_data = api.plant_list(user_id)
                plant_info = api.plant_info(plant_id)

                # device_data = []
                # for device in plant_info.get('deviceList'):
                #     device_sn = device['deviceSn']
                #
                #     mix_info = api.mix_info(int(device_sn))
                #     mix_total = api.inverter_data(int(device_sn))
                #
                #     device_data.append(device)
                #
                #     print(mix_info)
                #     print(mix_total)

                output_data.update(
                    {
                        'plantData': {
                            'cod2Reduction': plant_info.get('Co2Reduction'),  # CO2 Reduction %
                            'nominalPower': plant_info.get('nominal_Power'),  # Nominal Power (w)
                            'totalEnergy': plant_info.get('totalEnergy'),  # Solar Energy Total (kw)
                            'todayEnergy': plant_info.get('todayEnergy'),  # Solar Energy Today (kw)
                            'userId': user_id,
                            'plantId': plant_id
                        }
                    }
                )

        return output_data


    def login(self, **kwargs) -> dict:
        pre_login.send(sender=self.__class__)
        data = super(GrowattWeb, self).login(self.username, self.password, self.is_password_hashed)
        if data['success']:
            self.logged_in = True
        post_login.send(sender=self.__class__, data=data)
        return data

    def logout(self):
        pre_logout.send(sender=self.__class__)
        self.session.get(self.get_url("logout.do"))
        self.logged_in = False
        post_logout.send(sender=self.__class__)

    def firmware_check(self, fw_version: str):
        response = self.session.post(
            self.get_url('ftp.do'),
            params={
                'action': 'checkFirmwareVersion',
                'deviceTypeIndicate': '11',
                'firmwareVersion': fw_version,
            },
        )
        data = json.loads(response.content.decode('utf-8'))
        return data

    def firmware_update(self, data_log_sn: str):
        response = self.session.post(
            self.get_url('ftp.do'), params={'action': 'updateFirmware', 'dataLogSn': data_log_sn}
        )
        data = json.loads(response.content.decode('utf-8'))
        return data

    def restart_wifi(self, data_log_sn: str):
        response = self.session.post(
            self.get_url('ftp.do'), params={'action': 'restartDatalog', 'dataLogSn': data_log_sn}
        )
        data = json.loads(response.content.decode('utf-8'))
        return data

    def clear_data_wifi(self, data_log_sn: str):
        response = self.session.post(
            self.get_url('ftp.do'), params={'action': 'clearDatalog', 'dataLogSn': data_log_sn}
        )
        data = json.loads(response.content.decode('utf-8'))
        return data
