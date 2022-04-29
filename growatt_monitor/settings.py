#  -*- coding: utf-8 -*-

from pathlib import PurePath
from typing import Tuple

__base_dir__ = PurePath(__file__).parent.parent

#############################
# Global settings           #
#############################

DEBUG: bool = False

SETTINGS_STRICT: bool = False

BASE_DIR = str(__base_dir__)

#############################
# CASHES                    #
#############################

CACHES = {
    'default': {
        'BACKEND': 'RoundBox.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    },
    # 'default': {
    #     'BACKEND': 'RoundBox.core.cache.backends.filebased.FileBasedCache',
    #     'LOCATION': '/var/tmp/roundbox_cache',
    # },
    # 'default': {
    #     'BACKEND': 'RoundBox.core.cache.backends.dummy.DummyCache',
    # }
}

# Local time zone for this installation. All choices can be found here:
# https://en.wikipedia.org/wiki/List_of_tz_zones_by_name (although not all
# systems may support all possibilities). When USE_TZ is True, this is
# interpreted as the default user time zone.
TIME_ZONE: str = 'Europa/Bucharest'

# People who get code error notifications. In the format
# [('Full Name', 'email@example.com'), ('Full Name', 'anotheremail@example.com')]
ADMINS: list = []

# Email address that error messages come from.
SERVER_EMAIL: str = "root@localhost"

# The email backend to use. For possible shortcuts see django.core.mail.
# The default is to use the SMTP backend.
# Third-party backends can be specified by providing a Python path
# to a module that defines an EmailBackend class.
EMAIL_BACKEND: str = "RoundBox.core.mail.backends.smtp.EmailBackend"

# Optional SMTP authentication information for EMAIL_HOST.
EMAIL_HOST_USER: str = ""
EMAIL_HOST_PASSWORD: str = ""
EMAIL_START_TLS: bool = False
EMAIL_SSL: bool = True
EMAIL_OAUTH2: str | None = None

# Host for sending email.
EMAIL_HOST: str = "smtp.gmail.com"
# Port for sending email. For Gmail SMTP port (TLS) 587 and for Gmail SMTP port (SSL) 465
EMAIL_PORT: str = "587" if EMAIL_START_TLS else "465"
# Whether to send SMTP 'Date' header in the local time zone or in UTC.
EMAIL_USE_LOCALTIME: bool = False

EMAIL_USE_DKIM: bool = False
EMAIL_DKIM_DOMAIN: str | None = None
EMAIL_DKIM_SELECTOR: str | None = None
EMAIL_DKIM_KEY_FILE: str | None = None
EMAIL_DKIM_INCLUDE_HEADERS: list | None = None

###########
# LOGGING #
###########

# The callable to use to configure logging
LOGGING_CONFIG: str = 'logging.config.dictConfig'

# Custom logging configuration.
LOGGING: dict = {}

LOG_DIR = "log/"

INSTALLED_APPS: Tuple[str, ...] = (
    'growatt_proxy',
    'growatt_web_api',
    'open_weather_map',
    'pvoutput',
    'influxdb',
)
