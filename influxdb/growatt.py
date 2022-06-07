#  -*- coding: utf-8 -*-

from datetime import datetime, timezone
from pprint import pprint

from RoundBox.conf.app_settings import app_settings

from .influxdb import InfluxDB


class GrowattInfluxDB(InfluxDB):
    def __init(self, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        :return:
        """
        super().__init__(*args, **kwargs)

    def build_fields(self, data) -> dict:

        measurements = {}
        for field in data:

            try:
                value = float(field.native_value)
            except:
                pass

            measurements.update({field.api_key: value})
        return measurements

    def process_data(self, entities):
        """

        :param entities:
        :return:
        """
        data_buffer = []

        totals = entities.get('total')
        devices = entities.get('devices')

        time = datetime.now(timezone.utc)

        for total in totals:

            tags = {'plant_name': total.plant_name, 'plant_id': total.plant_id}
            fields = self.build_fields(total.totals)

            point = self.create_point(
                measurement='GrowattPV', tags=tags, fields=fields, time=time
            )

            data_buffer.append(point)

        for device in devices:

            tags = {
                'plant_name': device.plant_name,
                'plant_id': device.plant_id,
                'device_alias': device.device_alias,
                'serial_number': device.serial_number,
            }
            fields = self.build_fields(device.sensors)

            point = self.create_point(
                measurement='GrowattPV', tags=tags, fields=fields, time=time
            )

            data_buffer.append(point)

        return data_buffer
