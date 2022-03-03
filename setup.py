#!/usr/bin/env python
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

import setuptools
from setuptools import setup


def parse_requirements(filename):
    """ load requirements from a pip requirements file """
    lineiter = (line.strip() for line in open(filename))
    return [line for line in lineiter if line and not line.startswith("#")]


with open("README.md", "r") as fh:
    long_description = fh.read()

install_reqs = parse_requirements('requirements.txt')
reqs = install_reqs

setup(
      name='Growatt Monitor',
      version='1.0',
      description='Growatt Monitor implementation in Python, using the Growatt API server',
      license='GPL-3',
      author='Constantin Zaharia',
      author_email='constantin.zaharia@github.com',
      url='https://github.com/soulraven/growatt-monitor',
      packages=setuptools.find_packages(),
      install_requires=reqs,
      provides=['Growatt-monitor'],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Topic :: Software Development :: Libraries',
          'License :: OSI Approved :: GPLv3 License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3.9',
          'Programming Language :: Python :: 3.10',
      ],
      zip_safe=True
)
