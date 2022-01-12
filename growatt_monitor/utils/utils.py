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
import argparse
from importlib import import_module


def load_arguments():
    """Load arguments used in shell instance
    :return: An objects with argument name properties
    """
    parser = argparse.ArgumentParser(prog='Growatt Monitor', description="Using Growatt public server get the "
                                                                         "information about your own photovoltaic "
                                                                         "power plant")

    parser.add_argument("-d", "--debug", type=bool, default=False, help="Debug the running application")
    parser.add_argument('-auth-type', '--auth-type', type=str, default=None, help="Authentication type on the API "
                                                                                  "service")
    parser.add_argument("-u", "--username", type=str, default=None, help="Growatt username account")
    parser.add_argument("-p", "--password", type=str, default=None, help="Growatt password account")
    parser.add_argument("-key", "--api-key-token", type=str, default=None, help="Growatt API KEY TOKEN")
    parser.add_argument("-plantId", "--plant-id", type=int, default=None, help="ID of the plant that you want to get "
                                                                               "the information")
    parser.add_argument("-userId", "--user-id", type=int, default=None, help="ID of the logged user")
    parser.add_argument("-inverterId", "--inverter-id", type=list, nargs="+", help="List of you Growatt inverters, "
                                                                                   "delimited by space")
    parser.add_argument('--version', action='version', version='%(prog)s 1.0')

    return parser.parse_args()


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
