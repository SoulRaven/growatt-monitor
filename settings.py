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

from typing import Tuple

DEBUG: bool = True

##################
# Growatt server #
##################

# Growatt unofficial API endpoint based on engineered the API from the Growatt mobile app
GROWATT_ENDPOINT_WEB_API: str = 'https://server.growatt.com/'

# Growatt official API
GROWATT_ENDPOINT_API: str = 'https://test.growatt.com/v1/'

# In the future is possible that Growatt will change this
GROWATT_TEST_API_KEY_TOKEN = '6eb6f069523055a339d71e5b1f6c88cc'

####################################
# Growatt user authentication data #
####################################

GROWATT_AUTH_TYPE: str = 'auth'

GROWATT_API_KEY_TOKEN: str = ""

GROWATT_USERNAME: str = ""
GROWATT_PASSWORD: str = ""

####################################
# OpenWeatherMap API KEY           #
####################################

OWM_API_KEY: str = ""
OWM_LAT: float = 0.0
OWN_LON: float = 0.0

####################################
# PVOutput API KEY and SYSTEMS ID  #
####################################

PV_OUTPUT_KEY: str = ""

PV_OUTPUT_SYSTEM_ID: int = 0

####################################
# InfluxDB server settings         #
####################################
INFLUXDB_ENABLE: bool = False
INFLUXDB_SSL: bool = False
INFLUXDB_HOST: str = 'localhost'
INFLUXDB_PORT: int = 8086
INFLUXDB_URL: str = f"{'https' if INFLUXDB_SSL else 'http'}://{INFLUXDB_HOST}:{INFLUXDB_PORT}"
INFLUXDB_TOKEN: str = "my-token"
INFLUXDB_ORG: str = "my-org"

####################################
# InfluxDB default settings        #
####################################
INFLUXDB_BATH_SIZE: int = 500
INFLUXDB_FLUSH_INTERVAL: int = 10_000
INFLUXDB_JITTER_INTERVAL: int = 2_000
INFLUXDB_RETRY_INTERVAL: int = 5_000
INFLUXDB_MAX_RETRIES: int = 5
INFLUXDB_MAX_RETRY_DELAY: int = 30_000
INFLUXDB_EXPONENTIAL_BASE: int = 2

####################################
# Growatt Proxy server             #
####################################
GROWATT_PROXY_BIND_IP: str = "default"  # default means that the server will listen on all interfaces, and the IP is: 0.0.0.0
GROWATT_PROXY_BIND_PORT: int = 5279  # Default Growatt server port

GROWATT_REMOTE_IP: str = "47.91.67.66"
GROWATT_REMOTE_PORT: int = 5279

GROWATT_BLOCK_CMD: bool = False  # Inverter and Shine configure commands
GROWATT_NO_IP_CHANGE: bool = False  # Allow IP change if needed

GROWATT_MIN_REC_LENGTH: int = 100  # Minimum length of the Growatt record

GROWATT_COMPAT: bool = False

GROWATT_INVERTER_TYPE: str = "default"  # specify the inverter type default (spf, sph)

# Local time zone for this installation. All choices can be found here:
# https://en.wikipedia.org/wiki/List_of_tz_zones_by_name (although not all
# systems may support all possibilities). When USE_TZ is True, this is
# interpreted as the default user time zone.
TIME_ZONE: str = 'Europa/Bucharest'

#############################
# Global settings           #
#############################

# how many seconds each task will be delayed from the next task
SCHEDULE_DELAY_TASKS: int = 50

# People who get code error notifications. In the format
# [('Full Name', 'email@example.com'), ('Full Name', 'anotheremail@example.com')]
ADMINS: list = []

# Email address that error messages come from.
SERVER_EMAIL: str = "root@localhost"

# The email backend to use. For possible shortcuts see django.core.mail.
# The default is to use the SMTP backend.
# Third-party backends can be specified by providing a Python path
# to a module that defines an EmailBackend class.
EMAIL_BACKEND: str = "growatt_monitor.core.mail.backends.smtp.EmailBackend"

# Optional SMTP authentication information for EMAIL_HOST.
EMAIL_HOST_USER: str = ""
EMAIL_HOST_PASSWORD: str = ""
EMAIL_START_TLS: bool = False
EMAIL_SSL: bool = True
EMAIL_OAUTH2: str = None

# Host for sending email.
EMAIL_HOST: str = "smtp.gmail.com"
# Port for sending email. For Gmail SMTP port (TLS) 587 and for Gmail SMTP port (SSL) 465
EMAIL_PORT: str = "587" if EMAIL_START_TLS else "465"
# Whether to send SMTP 'Date' header in the local time zone or in UTC.
EMAIL_USE_LOCALTIME: bool = False

EMAIL_USE_DKIM: bool = False
EMAIL_DKIM_DOMAIN: str = None
EMAIL_DKIM_SELECTOR: str = None
EMAIL_DKIM_KEY_FILE: str = None
EMAIL_DKIM_INCLUDE_HEADERS: list = None

###########
# LOGGING #
###########

# The callable to use to configure logging
LOGGING_CONFIG: str = 'logging.config.dictConfig'

# Custom logging configuration.
LOGGING: dict = {}

# Loguru section
LOGURU: dict = {}

INSTALLED_APPS: Tuple[str, ...] = (
    'growatt_proxy',
    'growatt_web_api',
    'open_weather_map',
)
