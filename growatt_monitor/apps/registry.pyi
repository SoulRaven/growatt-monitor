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

class Apps:

    def __init__(self, installed_apps: dict = ()):
        """

        """
        self.apps_ready: bool = None
        self.ready_event = None
        self.app_configs: tuple = None
        self.loading: bool = None
        self._lock: bool = None
        self.ready: bool = None

    def populate(self, installed_apps=None, call_ready=False):
        """Load application configurations.
        Import each application module.
        It is thread-safe and idempotent, but not reentrant.

        # Changes from original:
          - added the call_ready attribute, to switch off/on the calling of ready method

        :param installed_apps:
        :param call_ready:
        :return:
        """

    def get_app_configs(self):
        """

        :return:
        """

    def check_apps_ready(self):
        """

        :return:
        """

    def get_app_config(self, param: str) -> tuple:
        """

        :param param:
        :return:
        """


apps: Apps = Apps
