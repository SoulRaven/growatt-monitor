#  -*- coding: utf-8 -*-

from RoundBox.conf.app_settings import app_settings

from pprint import pprint
from .influxdb import InfluxDB


class GrowattInfluxDB(InfluxDB):
    def __init(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def tags_for_measurements(self, data) -> dict:
        """

        :param data:
        :return:
        """
        tags = {}

        for tag in data:
            # print(tag.device_info)
            tags.update(
                {
                    'plantName': tag.device_info.get('plant_name'),
                    'plantID': tag.device_info.get('plant_id'),
                    'serial_number': tag.probe.get_data('serialNum'),
                    'device_mode': tag.probe.get_data('storageType'),
                }
            )

        return tags

    def fields_for_measurement(self, data) -> dict:

        measurements = {}
        for field in data:
            measurements.update({field.entity_description.key: field.native_value})
        return measurements

    def process_data(self, entities):
        """

        :param entities:
        :return:
        """
        data = []

        total = entities.get('total')
        devices = entities.get('devices')

        for device in total:
            print(device)

        # for key, val in devices.items():
        #     _device = {
        #         "measurement": 'GrowattPV',
        #         "tags": self.tags_for_measurements(val),
        #         "fields": self.fields_for_measurement(val),
        #     }
        #     data.append(_device)

        # data_total = {
        #     "measurement": 'GrowattPV',
        #     "tags": self.tags_for_measurements(total),
        #     "fields": self.fields_for_measurement(total),
        # }
        #
        # data.append(data_total)
        return data
