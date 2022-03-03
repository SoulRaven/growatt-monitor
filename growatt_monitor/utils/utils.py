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
import re
import argparse
import textwrap
import pkg_resources
import pathlib

from functools import lru_cache
from importlib import import_module

from growatt_monitor.core.exceptions import MissingInstalledPackage


def load_arguments():
    """Load arguments used in shell instance
    :return: An objects with argument name properties
    """
    parser = argparse.ArgumentParser(prog='Growatt Monitor', description="Using Growatt public server get the "
                                                                         "information about your own photovoltaic "
                                                                         "power plant",
                                     epilog="For more information read the documentation")

    parser.add_argument("--debug", type=bool, default=False, help="Debug the running application")

    parser.add_argument('--auth-type', type=str, default=None, help="Authentication type on the API service")
    parser.add_argument("--username", type=str, default="", help="Growatt username account")
    parser.add_argument("--password", type=str, default="", help="Growatt password account")
    parser.add_argument("--api-key-token", type=str, default="", help="Growatt API KEY TOKEN")
    parser.add_argument("--plant-id", type=int, default=0, help="ID of the plant that you want to get the "
                                                                "information")
    parser.add_argument("--user-id", type=int, default=None, help="ID of the logged user")
    parser.add_argument("--inverter-id", type=list, nargs="+", help="List of you Growatt inverters, delimited by space")

    parser.add_argument("--owm-key", type=str, default="", help="API key from Open Weather Map")
    parser.add_argument("--owm-lat", type=float, default=0.0, help="Latitude location for Open Weather Map")
    parser.add_argument("--owm-lon", type=float, default=0.0, help="Longitude location for Open Weather Map")

    parser.add_argument("--pv-output-key", type=str, default="", help="API Key from PVOutput")
    parser.add_argument("--pv-output-system-id", type=int, default=0, help="System ID from PVOutput")

    parser.add_argument("--influxdb-url", type=str, default="http://localhost:8086", help="InfluxDB URL path")
    parser.add_argument("--influxdb-token", type=str, default="my-token", help="InfluxDB token")
    parser.add_argument("--influxdb-org", type=str, default="my-org", help="Influxdb organization")

    parser.add_argument('--version', action='version', version='%(prog)s 1.0')

    return parser.parse_known_args()


def import_string(dotted_path):
    """ Import a dotted module path and return the attribute/class designated by the
        last name in the path. Raise ImportError if the import failed.
    """
    try:
        module_path, class_name = dotted_path.rsplit('.', 1)
    except ValueError as err:
        raise ImportError("%s doesn't look like a module path" % dotted_path) from err

    module = import_module(module_path)

    try:
        return getattr(module, class_name)
    except AttributeError as err:
        raise ImportError('Module "%s" does not define a "%s" attribute/class' % (
            module_path, class_name)
                          ) from err


def format_multi_line(prefix, string, size=80):
    """Formats multi-line data

    :param prefix:
    :param string:
    :param size:
    :return:
    """
    size -= len(prefix)
    if isinstance(string, bytes):
        string = ''.join(r'\x{:02x}'.format(byte) for byte in string)
        if size % 2:
            size -= 1
    return '\n'.join([prefix + line for line in textwrap.wrap(string, size)])


@lru_cache
def read_requirements() -> dict:
    """

    :return:
    """

    try:
        with pathlib.Path('requirements.txt').open(mode='rt', encoding='UTF-8') as f:
            line = f.read().splitlines()

        content = {}
        for kv in line:
            k, v = re.split(r'==|>=', kv)
            content.update({k: v})

        return content
    except IOError:
        return {}


def check_dependency():
    """

    :return:
    """
    installed_packages = {d.project_name: d.version for d in pkg_resources.working_set}
    requirement_list = read_requirements()

    missing_packages = set(requirement_list.items()) - set(installed_packages.items())
    if missing_packages:
        package = ", ".join(f"{package}({_})" for package, _ in missing_packages)
        raise MissingInstalledPackage(package)
