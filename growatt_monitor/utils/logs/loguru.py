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
import os
import sys
from threading import RLock
from itertools import chain
from typing import List, Dict

from loguru import logger

from growatt_monitor.conf import settings


def only_debug():
    def is_level(record):
        return record['level'].name == 'DEBUG' and settings.DEBUG

    return is_level


def only_info():
    def is_level(record):
        return record['level'].name in ('INFO', 'DEBUG')

    return is_level


DEFAULT_LOGURU: Dict = {
    "handlers": [
        # {
        #     "sink": sys.stderr,
        #     "enqueue": True,
        #     "colorize": True,
        #     "backtrace": True,
        #     "catch": True,
        #     "filter": only_debug(),
        #     "level": logging.DEBUG,
        #     "format": "{time:YYYY-MM-DDTHH:mm:ss.SSS!UTC}Z <lvl>{level: <8}</lvl>{level.icon} {name}: <lvl>{message}</lvl>",
        # },
        {
            "sink": sys.stderr,
            "enqueue": True,
            "colorize": True,
            "backtrace": True,
            "catch": True,
            # "filter": only_info(),
            "level": logging.INFO,
            "format": "{time:YYYY-MM-DDTHH:mm:ss.SSS!UTC}Z <lvl>{level: <6}</lvl>{name}:{function}:{line}: <lvl>{message}</lvl>",
        },
        {
            "sink": "log/loguru.log",
            "enqueue": True,
            "rotation": '5MB',
            "retention": 9,
            "filter": only_debug(),
            "level": logging.DEBUG,
            "format": '{time} {level} {message}',
        },
    ],
    'extra': {},
    'notifiers': {
        'smtp': {
            'subject': 'New email from loguru',
            'from': '[USER@HOSTNAME]',
            'host': 'localhost',
            'port': 25,
            'tls': False,
            'ssl': False,
            'html': False,
        },
        'gitter': {'token': '', 'room_id': ''},
        'gmail': {
            'subject': "New email from 'notifiers'!",
            'from': '<USERNAME@HOST>',
            'host': 'smtp.gmail.com',
            'port': 587,
            'tls': True,
            'ssl': False,
            'html': False,
            'login': True,
        },
        'hipchat': {},
        'join': {'apikey': ''},
        'mailgun': {},
        'telegram': {'token': '', 'chat_id': ''},
    },
}

special_chars_code = {
    'D': '30',  # Disabled
    'R': '31',  # Red
    'G': '32',  # Green
    'Y': '33',  # Yellow
    'B': '34',  # Blue
    'P': '35',  # Purple
    'C': '36',  # Cyan
    'W': '37',  # White
}

special_chars = {
    'CC': '\033[0m',  # Clear Color
    'CN': '\033[2K',  # Clear Line
    'CR': '\r',  # To First Line
}


def get_special_char(key=None, char_type=1) -> str:
    """
    char_type
    ```
    0 = normal
    1 = bold (light)
    2 = dark
    3 = italic
    4 = underline
    5 = blink
    6 = blink again (?)
    7 = reverse
    ```
    """
    special_char = special_chars.get(key)
    if special_char is not None:
        return special_char

    char_code = special_chars_code.get(key)
    if key is not None and char_code is not None:
        return f'\033[{char_code};{char_type}m'

    return f'\033[{char_type}m'


for code in special_chars_code:
    for i in range(1, 9 + 1):
        special_chars[f'{code}{i}'] = get_special_char(code, i)


class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


logging.basicConfig(handlers=[InterceptHandler()], level=20)


class Logger:
    def __init__(self, loguru_settings=settings.LOGURU, level='DEBUG'):
        self._lock = RLock()

        self.special_chars = special_chars

        self.logger = logger

        self.extra_config = {
            'CC': self.special_chars['CC'],
            'CN': self.special_chars['CN'],
            'CR': self.special_chars['CR'],
        }

        self.config = dict(chain(DEFAULT_LOGURU.items(), loguru_settings.items()))
        self.config['extra'].update(self.extra_config)

        notifiers = self.config.get('notifiers')
        if notifiers:
            self.config_notifiers(notifiers)
            self.config.pop('notifiers')

        self.logger.remove()
        self.logger.configure(**self.config)

        # self.logger.add(sys.stderr, colorize=True,
        #                 format="{time:YYYY-MM-DDTHH:mm:ss.SSS!UTC}Z {name}.{module}.{function}({line}) {level}: {message}", level=level)

    def config_notifiers(self, notifiers: dict = {}):
        """

        :return:
        """

        from notifiers.logging import NotificationHandler

        sink_notifiers = {}

        for _type, notify in notifiers.items():
            sink = {}
            match _type:
                case 'smtp':
                    handler = NotificationHandler("gmail", defaults=notify)
                    sink = {'sink': handler, 'level': 'INFO', 'enqueue': True}
                case 'gitter':
                    pass
                case 'gmail':
                    pass
                case 'hipchat':
                    pass
                case 'join':
                    pass
                case 'mailgun':
                    pass
                case 'pagerduty':
                    pass
                case 'popcorn_notify':
                    pass
                case 'pushbullet':
                    pass
                case 'pushover':
                    pass
                case 'simplepush':
                    pass
                case 'slack':
                    pass
                case 'status_page':
                    pass
                case 'telegram':
                    handler = NotificationHandler("gmail", defaults={})
                    sink = {}
                case 'twilio':
                    pass
                case 'zulip':
                    pass
                case _:
                    pass

            if sink:
                sink_notifiers.update(sink)

    def replace(self, message):
        columns, _ = os.get_terminal_size()

        if len(message) > columns:
            message = message[: columns - 3] + '...'

        with self._lock:
            sys.stdout.write(
                f'{self.extra_config["CN"]}{message}{self.extra_config["CC"]}{self.extra_config["CR"]}'
            )
            sys.stdout.flush()

    def log(self, message, level='INFO'):
        self.logger.log(level, message)
