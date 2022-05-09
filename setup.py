#!/usr/bin/env python
#  -*- coding: utf-8 -*-

import os
import site
import sys
from distutils.sysconfig import get_python_lib

from setuptools import find_packages, setup

from growatt_monitor.version import __version__

# Allow editable install into user site directory.
# See https://github.com/pypa/pip/issues/7953.
site.ENABLE_USER_SITE = "--user" in sys.argv[1:]

# Warn if we are installing over top of an existing installation. This can
# cause issues where files that were deleted from a more recent Django are
# still present in site-packages. See #18115.
overlay_warning = False
if "install" in sys.argv:
    lib_paths = [get_python_lib()]
    if lib_paths[0].startswith("/usr/lib/"):
        # We have to try also with an explicit prefix of /usr/local in order to
        # catch Debian's custom user site-packages directory.
        lib_paths.append(get_python_lib(prefix="/usr/local"))
    for lib_path in lib_paths:
        existing_path = os.path.abspath(os.path.join(lib_path, "django"))
        if os.path.exists(existing_path):
            # We note the need for the warning here, but present it after the
            # command is run, so it's more likely to be seen.
            overlay_warning = True
            break


def parse_requirements(filename):
    """load requirements from a pip requirements file"""
    lineiter = (line.strip() for line in open(filename))
    return [line for line in lineiter if line and not line.startswith("#")]


with open("README.md", "r") as fh:
    long_description = fh.read()

install_reqs = parse_requirements('requirements.txt')

setup(
    name='Growatt Monitor',
    version=__version__,
    description='Growatt implementation for monitoring and notification',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='GPL-3',
    author='Constantin Zaharia',
    author_email='constantin.zaharia@github.com',
    url='https://github.com/soulraven/growatt-monitor',
    packages=find_packages(),
    install_requires=install_reqs,
    provides=[],
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

if overlay_warning:
    sys.stderr.write(
        """
========
WARNING!
========
You have just installed Growatt Monitor over top of an existing
installation, without removing it first. Because of this,
your install may now include extraneous files from a
previous version that have since been removed from
Growatt Monitor. This is known to cause a variety of problems. You
should manually remove the
%(existing_path)s
directory and re-install Growatt Monitor.
"""
        % {"existing_path": existing_path}
    )
