#  -*- coding: utf-8 -*-
#
#              Copyright (C) 2018-2021 ProGeek
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
import functools

from growatt_monitor.conf import settings

log = logging.getLogger('growatt_logging')


def session_manager(f):

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        self = args[0]
        if self.auth_type == 'api_key':
            pass
        elif self.auth_type == 'auth':
            if not self.logged_in:
                self.login()

        if self.logged_in:
            output = f(*args, **kwargs)

        if self.auth_type == 'auth':
            if self.logged_in:
                self.logout()

        return output

    return wrapper
