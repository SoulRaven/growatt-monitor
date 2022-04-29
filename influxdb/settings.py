#  -*- coding: utf-8 -*-

####################################
# InfluxDB server settings         #
####################################
INFLUXDB_ENABLE: bool = False
INFLUXDB_SSL: bool = False
INFLUXDB_HOST: str = '10.10.13.69'
INFLUXDB_PORT: int = 8086
INFLUXDB_URL: str = f"{'https' if INFLUXDB_SSL else 'http'}://{INFLUXDB_HOST}:{INFLUXDB_PORT}"
INFLUXDB_GZIP: bool = True
INFLUXDB_TIMEOUT: int = 10_000
INFLUXDB_TOKEN: str = "my-token"
INFLUXDB_ORG: str = "my-org"

####################################
# InfluxDB default settings        #
####################################
INFLUXDB_BATH_SIZE: int = 500
INFLUXDB_FLUSH_INTERVAL: int = 10_000
INFLUXDB_JITTER_INTERVAL: int = 2_000
INFLUXDB_RETRY_INTERVAL: int = 5_000
INFLUXDB_MAX_RETRIES: int = 5
INFLUXDB_MAX_RETRY_DELAY: int = 30_000
INFLUXDB_EXPONENTIAL_BASE: int = 2
