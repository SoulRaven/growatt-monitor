#  -*- coding: utf-8 -*-

# @TODO: move this file, and find a propper location

import logging

from itertools import cycle  # to support "cycling" the iterator

from RoundBox.conf.project_settings import settings
from RoundBox.utils.utils import format_multi_line

log = logging.getLogger('growatt_logging')


def decrypt(crypt_data):
    ndecdata = len(crypt_data)

    # Create mask and convert to hexadecimal
    mask = "Growatt"
    hex_mask = ['{:02x}'.format(ord(x)) for x in mask]
    nmask = len(hex_mask)

    # start decrypt routine
    unscrambled = list(crypt_data[0:8])  # take unscramble header

    for i, j in zip(range(0, ndecdata - 8), cycle(range(0, nmask))):
        unscrambled = unscrambled + [crypt_data[i + 8] ^ int(hex_mask[j], 16)]

    result_string = "".join("{:02x}".format(n) for n in unscrambled)

    log.info("Growatt data decrypted V2")
    return result_string


def process_data(data):
    log.info("Growatt original Data:")
    log.info(format_multi_line("\t\t", data))

    header = "".join("{:02x}".format(n) for n in data[0:8])
    ndata = len(data)

    # set buffer detection to nodetect (for compat mode), will in auto-detection changed to no or yes
    buffered = "nodetect"

    # automatic detect protocol (decryption and protocol) only if compat = False!
    novalidrec = False

    if settings.GROWATT_COMPAT is False:
        if settings.DEBUG:
            log.debug("Growatt automatic protocol detection")
            log.debug("Growatt data record length {}".format(ndata))

        layout = "T" + header[6:8] + header[12:14] + header[14:16]
        if ndata > 375:
            layout = layout + "X"

        if settings.GROWATT_INVERTER_TYPE != "default":
            layout = layout + settings.GROWATT_INVERTER_TYPE.upper()

        if header[14:16] == "50":
            buffered = "yes"
        else:
            buffered = "no"

        if settings.DEBUG:
            log.debug("Layout: {}".format(layout))
        try:
            # does record layout record exists?
            test = conf.recorddict[layout]
        except:
            # try generic if generic record exist
            if settings.DEBUG:
                log.debug("No matching record layout found, try generic")
            if header[14:16] in ("04", "50"):
                layout = layout.replace(header[12:16], "NNNN")
                try:
                    # does generic record layout record exists?
                    test = conf.recorddict[layout]
                except:
                    # no valid record fall back on old processing?
                    if settings.DEBUG:
                        log.debug("No matching record layout found, standard processing performed")
                    layout = "none"
                    novalidrec = True
            else:
                novalidrec = True

        if settings.DEBUG:
            log.debug("Record layout used : {}".format(layout))
