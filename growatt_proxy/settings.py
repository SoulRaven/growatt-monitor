#  -*- coding: utf-8 -*-

####################################
# Growatt Proxy server             #
####################################
GROWATT_PROXY_BIND_IP: str = "default"  # default means that the server will listen on all interfaces, and the IP is: 0.0.0.0
GROWATT_PROXY_BIND_PORT: int = 5279  # Default Growatt server port

GROWATT_REMOTE_IP: str = "47.91.67.66"
GROWATT_REMOTE_PORT: int = 5279

GROWATT_BLOCK_CMD: bool = False  # Inverter and Shine configure commands
GROWATT_NO_IP_CHANGE: bool = False  # Allow IP change if needed

GROWATT_MIN_REC_LENGTH: int = 100  # Minimum length of the Growatt record

GROWATT_COMPAT: bool = False

GROWATT_INVERTER_TYPE: str = "default"  # specify the inverter type default (spf, sph)
