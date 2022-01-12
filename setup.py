#!/usr/bin/env python
#  -*- coding: utf-8 -*-
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

import setuptools
from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
      name='Growatt Monitor',
      version='1.0',
      description='Growatt Monitor implementation in Python, using the Growatt API server',
      license='GPL-3',
      author='Constantin Zaharia',
      author_email='constantin.zaharia@github.com',
      url='https://github.com/soulraven/growatt-monitor',
      packages=setuptools.find_packages(),
      install_requires=[
            'pymodbus (>= 2.4.0)',
            "requests",
      ],
      provides=['Growatt-monitor'],
      )
