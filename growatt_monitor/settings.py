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

DEBUG = True

##################
# Growatt server #
##################

# Growatt unofficial API endpoint based on engineered the API from the Growatt mobile app
GROWATT_ENDPOINT_WEB_API = 'https://server.growatt.com/'

# Growatt official API
GROWATT_ENDPOINT_API = 'https://test.growatt.com/v1/'

# In the future is possible that Growatt will change this
GROWATT_TEST_API_KEY_TOKEN = '6eb6f069523055a339d71e5b1f6c88cc'

####################################
# Growatt user authentication data #
####################################

GROWATT_AUTH_TYPE = 'auth'

GROWATT_API_KEY_TOKEN = None

GROWATT_USERNAME = None
GROWATT_PASSWORD = None

###########
# LOGGING #
###########

# The callable to use to configure logging
LOGGING_CONFIG = 'logging.config.dictConfig'

# Custom logging configuration.
LOGGING = {}
