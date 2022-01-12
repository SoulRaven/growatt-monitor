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

import datetime
import logging

from growatt_monitor.conf import settings
from growatt_monitor.core.exceptions import ImproperlyConfigured

from growattServer import GrowattApi, hash_password

log = logging.getLogger('growatt_logging')


class GrowattWeb(GrowattApi):

    def __init__(self, is_password_hashed=False, *args, **kwargs):
        super(GrowattWeb, self).__init__()
        self.logged_in = False

        self.username = kwargs.get('username', getattr(settings, 'GROWATT_USERNAME', None))
        self.password = kwargs.get('password', getattr(settings, 'GROWATT_PASSWORD', None))

        if any(x is None for x in [self.username, self.password]):
            raise ImproperlyConfigured("Username or password are not defined in main script arguments")

        if not is_password_hashed:
            self.password = hash_password(self.password)

        # setup endpoint
        self.server_url = getattr(settings, 'GROWATT_ENDPOINT_WEB_API')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.logged_in:
            self.logout()

    def login(self, **kwargs):
        data = super(GrowattWeb, self).login(self.username, self.password, True)
        if data['success']:
            self.logged_in = True
        return data

    def logout(self):
        self.session.get(self.get_url("logout.do"))
        self.logged_in = False
