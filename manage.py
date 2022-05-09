#!/usr/bin/env python3.10
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

import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('ROUNDBOX_SETTINGS_MODULE', 'growatt_monitor.settings')
    try:
        from RoundBox.core.cliparser import exec_from_cli
    except ImportError as exc:
        raise ImportError(
            "Couldn't import RoundBox. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    exec_from_cli(sys.argv)


if __name__ == '__main__':
    main()
