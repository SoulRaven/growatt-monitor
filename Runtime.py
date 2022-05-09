#  -*- coding: utf-8 -*-


import asyncio
import logging
from datetime import datetime

import aiohttp
from influxdb_client import InfluxDBClient, WriteOptions
from roundBox.conf import settings
from roundBox.core.pvoutput.PVOutputAPI import PVOutputAPI
from roundBox.core.web.GrowattWeb import GrowattWeb, Timespan

from pvoutput.asyncio import PVOutput

log = logging.getLogger('growatt_logging')


class Runtime:
    def __init__(self, *args, **kwargs):

        # first thing import the signals
        import signals  # noqa

        # Growatt CLI args
        self.growatt_username = kwargs.get('username', getattr(settings, 'GROWATT_USERNAME', ""))
        self.growatt_password = kwargs.get('password', getattr(settings, 'GROWATT_PASSWORD', ""))

        self.pvoutput_key = kwargs.get('pv_output_key', getattr(settings, 'PV_OUTPUT_KEY', ""))
        self.pvoutput_system_id = kwargs.get(
            'pv_output_system_id', getattr(settings, 'PV_OUTPUT_SYSTEM_ID', 0)
        )

        if self.pvoutput_key:
            self.pvoutput = PVOutputAPI(self.pvoutput_key, self.pvoutput_system_id)

        # check and init the Open Weather Map
        owm_key = kwargs.get('owm_key') or getattr(settings, 'OWM_API_KEY')
        owm_lat = kwargs.get('owm_lat') or getattr(settings, 'OWM_LAT')
        owm_lon = kwargs.get('owm_lon') or getattr(settings, 'OWN_LON')
        if owm_key:
            self.owm = False

        self.influxdb_url = kwargs.get('influxdb_url') or getattr(settings, 'INFLUXDB_URL')
        self.influxdb_token = kwargs.get('influxdb_token') or getattr(settings, 'INFLUXDB_TOKEN')
        self.influxdb_org = kwargs.get('influxdb_org') or getattr(settings, 'INFLUXDB_ORG')

    def run_schedule_task(self):
        log.info("Run schedule task")

        log.debug("Query open_weather_map")
        if self.owm:
            try:
                self.owm.get()
                self.owm.fresh = True
            except Exception as e:
                log.error('Getting weather: {}'.format(e))
                self.owm.fresh = False

        pv_data = {}
        with GrowattWeb(username=self.growatt_username, password=self.growatt_password) as api:
            data = api.login()
            if 'success' in data and data['success']:
                # TODO: Get only the first plant from a bigger list.
                #  In the future make this more costume
                plant_id = data['data'][0]['plantId']
                plant_info = api.plant_info(plant_id)
                plant_detail = api.plant_detail(plant_id, Timespan.day)
                device_list = api.device_list(plant_id)
                device_id = device_list[0]['deviceSn']
                inverter_detail = api.inverter_detail(device_id)

                # print(plant_detail)
                # print(plant_info)

        # if self.pvoutput_key:
        #     asyncio.run(self.upload_to_pvoutput(pv_data))

        # if settings.INFLUXDB_ENABLE:
        #     self.insert_to_influxdb()

    async def upload_to_pvoutput(self, data):
        data = {
            "v2": 500,  # power generation
            "v4": 450,  # power consumption
            "v5": self.owm.temperature,  # temperature
            "v6": 234.0,  # voltage
        }
        async with aiohttp.ClientSession() as session:
            pvo = PVOutput(
                apikey=self.pvoutput_key, systemid=self.pvoutput_system_id, session=session
            )
            await pvo.addstatus(data)

    def insert_to_influxdb(self):

        with InfluxDBClient(
            url=self.influxdb_url, token=self.influxdb_token, org=self.influxdb_org
        ) as _client:
            with _client.write_api(
                write_options=WriteOptions(
                    batch_size=settings.INFLUXDB_BATH_SIZE,
                    flush_interval=settings.INFLUXDB_FLUSH_INTERVAL,
                    jitter_interval=settings.INFLUXDB_JITTER_INTERVAL,
                    retry_interval=settings.INFLUXDB_RETRY_INTERVAL,
                    max_retries=settings.INFLUXDB_MAX_RETRIES,
                    max_retry_delay=settings.INFLUXDB_MAX_RETRY_DELAY,
                    exponential_base=settings.INFLUXDB_EXPONENTIAL_BASE,
                )
            ) as _write_client:
                pass

    def publish_to_mqtt(self):
        pass
