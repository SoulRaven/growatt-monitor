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

import functools
from loguru import logger

from growatt_monitor.conf import settings


def logger_wraps(*args, **kwargs):
    def wrapper(func):
        name = func.__name__

        @functools.wraps(func)
        def wrapped(*_args, **_kwargs):
            logger_ = logger.opt(depth=1)
            if settings.DEBUG:
                logger_.debug("Entering '{}' (args={}, kwargs={})", name, _args, _kwargs)
            result = func(*_args, **_kwargs)
            if settings.DEBUG:
                logger_.debug("Exiting '{}' (result={})", name, result)
            return result

        return wrapped

    return wrapper


