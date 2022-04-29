#!/usr/bin/env python
#  -*- coding: utf-8 -*-

import setuptools
from setuptools import setup

from growatt_monitor.version import __version__


def parse_requirements(filename):
    """load requirements from a pip requirements file"""
    lineiter = (line.strip() for line in open(filename))
    return [line for line in lineiter if line and not line.startswith("#")]


with open("README.md", "r") as fh:
    long_description = fh.read()

install_reqs = parse_requirements('requirements.txt')
reqs = install_reqs

setup(
    name='Growatt Monitor',
    version=__version__,
    description='Growatt Monitor implementation in Python, using the Growatt API server',
    long_description=long_description,
    long_description_content_type="text/markdown",
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
    zip_safe=True,
)
