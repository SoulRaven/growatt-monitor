#  -*- coding: utf-8 -*-

import logging
from datetime import datetime, timezone

from influxdb_client import InfluxDBClient, Point, WriteOptions
from influxdb_client.client.exceptions import InfluxDBError
from influxdb_client.client.write_api import ASYNCHRONOUS, SYNCHRONOUS
from RoundBox.conf.app_settings import app_settings
from urllib3 import Retry

logger = logging.getLogger(__name__)


class BatchingCallback:
    def success(self, conf: (str, str, str), data: str):
        """

        :param conf:
        :param data:
        :return:
        """
        print(f"Written batch: {conf}, data: {data}")

    def error(self, conf: (str, str, str), data: str, exception: InfluxDBError):
        """

        :param conf:
        :param data:
        :param exception:
        :return:
        """
        print(f"Cannot write batch: {conf}, data: {data} due: {exception}")

    def retry(self, conf: (str, str, str), data: str, exception: InfluxDBError):
        """

        :param conf:
        :param data:
        :param exception:
        :return:
        """
        print(f"Retryable error occurs for batch: {conf}, data: {data} retry: {exception}")


class InfluxDB:
    def __init__(self, url, token, org, dry=False, **kwargs):
        """

        :param url:
        :param token:
        :param org:
        :param kwargs:
        """

        self.dry = dry

        options = {
            'gzip': app_settings.INFLUXDB_GZIP,
            'timeout': app_settings.INFLUXDB_TIMEOUT,
            'connect': app_settings.INFLUXDB_CONNECT,
            'read': app_settings.INFLUXDB_READ,
            'redirect': app_settings.INFLUXDB_REDIRECT,
        }

        self.connection = self._connection(url=url, token=token, org=org, **options, **kwargs)

        if self.is_alive:
            self._write_api = self.connection.write_api(
                write_options=WriteOptions(write_type=SYNCHRONOUS)
            )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):

        if self.connection.ping():
            self._write_api.close()
            self.connection.close()
            logger.debug('InfluxDB connection is closed!')

    def _connection(self, url, token, org, gzip, timeout, connect, read, redirect, **kwargs):
        """Create an InfluxDB connection and test to make sure it works.
        We test with the get all users command.  If the address is bad it fails
        with a 404.  If the user doesn't have permission it fails with 401

        :return:
        """

        retries = Retry(connect=5, read=2, redirect=5)

        connection = InfluxDBClient(
            url=url,
            token=token,
            org=org,
            enable_gzip=gzip,
            timeout=timeout,
            retries=retries,
            **kwargs,
        )
        return connection

    def upload(self, data_points=None):
        """Uploads data points to InfluxDB

        :param data_points:
        :return:
        """

        if data_points is not None and len(data_points) > 0:
            if self.is_alive:
                self._write_api.write(bucket=app_settings.INFLUXDB_BUCKET, record=data_points)
                logger.info('Data upload on InfluxDB bucket')

    @property
    def is_alive(self):
        """

        :return:
        """
        return self.connection.ping() if self.connection else False

    def build_fields(self, data) -> list:
        """

        :return:
        """
        raise NotImplementedError('Subclasses must implement this')

    def create_point(self, measurement, time, fields, tags=None):
        """Helps enforce proper InfluxDB point creation

        :param measurement:
        :param time:
        :param fields:
        :param tags:
        :return:
        """

        # tags can be an empty dict
        if tags is None:
            tags = {}

        if not isinstance(measurement, str):
            raise TypeError('Measurement must be a string.')

        if not isinstance(time, datetime):
            raise TypeError('Time must be a datetime object.')

        if not isinstance(fields, dict):
            raise TypeError('Fields must be a dictionary.')
        elif len(fields) < 1:
            # there must be at least one field
            raise ValueError('Fields must contain at least one field.')

        if not isinstance(tags, dict):
            raise TypeError('Tags must be a dictionary.')

        # convert datetime object to string
        time = self._create_influx_time(time)

        point = {'tags': tags, 'time': time, 'fields': fields, 'measurement': measurement}

        return point

    def _create_influx_time(self, time):
        """Takes in a datetime object
        Returns a datetime string InfluxDB expects, in UTC

        :param time:
        :return:
        """
        # save as correct format in UTC timezone
        return time.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

    def process_data(self, data):
        """

        :param data:
        :return:
        """

        raise NotImplementedError('Implement this error in subclasses')
