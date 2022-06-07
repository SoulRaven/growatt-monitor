#  -*- coding: utf-8 -*-

####################################
# InfluxDB server settings         #
####################################
INFLUXDB_ENABLE: bool = False
INFLUXDB_SSL: bool = False
INFLUXDB_HOST: str = '10.10.13.69'
INFLUXDB_PORT: int = 8086
INFLUXDB_URL: str = (
    f"{'https' if INFLUXDB_SSL else 'http'}://{INFLUXDB_HOST}:{INFLUXDB_PORT}"
)
INFLUXDB_TOKEN: str = "ny9vODSDkg0VDZDE4J5DJ2Ul6MdSnlpZ70xbRLkqCF-w-b1skQj411CCIrCrnw9smnHWvD-vOfGSGLz4W8KGAA=="
INFLUXDB_ORG: str = "ProGeek"
INFLUXDB_BUCKET: str = 'energyMonitoring'

INFLUXDB_GZIP: bool = True
INFLUXDB_TIMEOUT: int = 10_000
INFLUXDB_CONNECT: int = 5
INFLUXDB_READ: int = 2
INFLUXDB_REDIRECT: int = 5

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
