#  -*- coding: utf-8 -*-
#
#  Copyright (C) 2020-2021 ProGeek
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

from growatt_monitor.conf import settings
from growatt_monitor.utils.hashable import hash_password
from growatt_monitor.core.exceptions import LoginError, GrowattApiError, ImproperlyConfigured

log = logging.getLogger('growatt_logging')


class SessionFactory:
    auth_type = None
    api_key = None
    username = None
    password = None

    endpoint = None

    headers = {
        'Content-Type': 'application/json'
    }

    logged_in = False

    def __init__(self, is_password_hashed=False, *args, **kwargs):

        self.session = requests.Session()

        self.username = kwargs.get('username', getattr(settings, 'GROWATT_USERNAME', None))
        self.password = kwargs.get('password', getattr(settings, 'GROWATT_PASSWORD', None))

        if any(x is None for x in [self.username, self.password]):
            raise ImproperlyConfigured("Username or password are not defined in main script arguments")

        if not is_password_hashed:
            self.password = hash_password(self.password)

        # setup endpoint
        self.endpoint = getattr(settings, 'GROWATT_ENDPOINT_WEB_API')

    def process_response(self, response):
        """
        Check and return the response, where we expect a "back" key with a
        "success" item.
        """

        if response.status_code != requests.codes.ok:
            log.exception("Request failed: %s" % response)
            raise GrowattApiError("Request failed: %s" % response)

        data = response.json()

        # every response begins with a 'back' key in the dictionary
        if "back" in data:
            result = data.get('back')

            # check if the success key is present and is TRUE
            if not ("success" in result and result["success"]):
                log.exception("Growatt backend server returned invalid response")
                raise GrowattApiError("Growatt backend server returned invalid response")
        else:

            if "success" in data and not data["success"]:
                log.exception("Growatt backend server returned invalid response")
                raise GrowattApiError("Growatt backend server returned invalid response")
            result = data

        return result

    def get_url(self, page):
        return f"{self.endpoint}{page}"
