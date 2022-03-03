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

import functools
import inspect


@functools.lru_cache(maxsize=512)
def _get_func_parameters(func, remove_first):
    parameters = tuple(inspect.signature(func).parameters.values())
    if remove_first:
        parameters = parameters[1:]
    return parameters


def _get_callable_parameters(meth_or_func):
    is_method = inspect.ismethod(meth_or_func)
    func = meth_or_func.__func__ if is_method else meth_or_func
    return _get_func_parameters(func, remove_first=is_method)


def func_accepts_kwargs(func):
    """Return True if function 'func' accepts keyword arguments **kwargs."""
    return any(
        p for p in _get_callable_parameters(func)
        if p.kind == p.VAR_KEYWORD
    )
