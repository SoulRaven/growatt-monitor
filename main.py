#!/usr/bin/env python3.10
#  -*- coding: utf-8 -*-


import sys
import os

from RoundBox import setup

os.environ.setdefault('ROUNDBOX_SETTINGS_MODULE', 'growatt_monitor.settings')

if __name__ == '__main__':

    try:
        setup()
    except KeyboardInterrupt:
        sys.exit(1)
