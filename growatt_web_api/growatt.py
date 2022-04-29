#  -*- coding: utf-8 -*-

import datetime
import json
import logging

from typing import Final, TypedDict
from dataclasses import dataclass

from RoundBox.apps import apps
from RoundBox.conf.project_settings import settings
from RoundBox.conf.app_settings import app_settings
from RoundBox.core.exceptions import ImproperlyConfigured
from RoundBox.core.hass.components.sensor import DeviceInfo, ExtraOptions
from RoundBox.utils import dt
from RoundBox.utils.throttle import Throttle

from growattServer import GrowattApi, hash_password, Timespan

from .sensor_types.sensor_entity_description import GrowattSensorEntityDescription
from .sensor_types.inverter import INVERTER_SENSOR_TYPES
from .sensor_types.mix import MIX_SENSOR_TYPES
from .sensor_types.storage import STORAGE_SENSOR_TYPES
from .sensor_types.tlx import TLX_SENSOR_TYPES
from .sensor_types.total import TOTAL_SENSOR_TYPES

from .signals import pre_login, post_login, pre_logout, post_logout, runtime_send

logger = logging.getLogger(__name__)

SCAN_INTERVAL = datetime.timedelta(minutes=1)


def get_device_list(api, username, password, plant_id=None):
    """Retrieve the device list for the selected plant.

    :param api:
    :param password:
    :param username:
    :param plant_id:
    :return:
    """

    plant_id = plant_id or getattr(app_settings, 'GROWATT_DEFAULT_PLANT_ID')
    plant_name = ''

    # Log in to api and fetch first plant if no plant id is defined.
    login_response = api.login(username, password)
    if (
        not login_response["success"]
        and login_response["msg"] == app_settings.LOGIN_INVALID_AUTH_CODE
    ):
        logger.error("Username, Password or URL may be incorrect!")
        return

    user_id = login_response["user"]["id"]
    # plant_info = api.plant_list(user_id)

    plant_info = login_response['data']
    if plant_id <= 0:
        _plant = plant_info[0]
        plant_id = _plant["plantId"]
        plant_name = _plant['plantName']
    else:
        for plant in plant_info:
            if int(plant['plantId']) == plant_id:
                plant_name = plant['plantName']

    # Get a list of devices for specified plant to add sensors for.
    devices = api.device_list(plant_id)

    return devices, plant_name, plant_id


def growatt_runtime(options) -> None:
    """

    :param options:
    :return:
    """

    username = options.get('username') or getattr(app_settings, 'GROWATT_USERNAME')
    password = options.get('password') or getattr(app_settings, 'GROWATT_PASSWORD')
    plant_id = options.get('plantId') or getattr(app_settings, 'GROWATT_DEFAULT_PLANT_ID')

    url = options.get('server') or getattr(app_settings, 'GROWATT_DEFAULT_URL')

    api = GrowattApi()
    api.server_url = url

    devices, plant_name, plant_id = get_device_list(api, username, password, plant_id)

    probe = GrowattData(api, username, password, plant_id, "total")

    if not probe.data:
        probe.update()
        logger.info('Growatt server update Plant total data')

    entities = {'total': [], 'devices': []}

    total = GrowattTotal(PlantInfo(plantId=plant_id, plantName=plant_name))

    for description in TOTAL_SENSOR_TYPES:
        data = probe.get_data(description.api_key)
        total.add_sensor(data, description)

    entities['total'].append(total)

    # Add sensors for each device in the specified plant.
    for device in devices:
        probe = GrowattData(api, username, password, device["deviceSn"], device["deviceType"])

        sensor_descriptions: tuple[GrowattSensorEntityDescription, ...] = ()
        match device["deviceType"]:
            case "inverter":
                sensor_descriptions = INVERTER_SENSOR_TYPES
            case "tlx":
                probe.plant_id = plant_id
                sensor_descriptions = TLX_SENSOR_TYPES
            case "storage":
                probe.plant_id = plant_id
                sensor_descriptions = STORAGE_SENSOR_TYPES
            case "mix":
                probe.plant_id = plant_id
                sensor_descriptions = MIX_SENSOR_TYPES
            case _:
                logger.debug(
                    "Device type %s was found but is not supported right now", device["deviceType"]
                )

        if not probe.data:
            probe.update()
            logger.info(f'Growatt server update for {device["deviceSn"]}')

        devices = GrowattAppliance(
            InverterInfo(device=device, plant_info=PlantInfo(plantName=plant_name, plantId=plant_id))
        )

        for description in sensor_descriptions:
            data = probe.get_data(description.api_key)
            devices.add_sensor(data, description)

        entities['devices'].append(devices)

    runtime_send.send(sender=growatt_runtime, entities=entities)


@dataclass
class PlantInfo:
    plantName: str | None
    plantId: str | None


@dataclass
class InverterInfo:

    device: dict | None
    plant_info: PlantInfo | None


class GrowattSensor:
    def __init__(self, value, description: GrowattSensorEntityDescription, extra_options=None):
        """

        :param value:
        :param description:
        :param extra_options:
        """

        self.value = value
        self.entity_description = description
        self._attr_extra_options = extra_options

        self._attr_name = description.name
        self._attr_key = description.key
        self._attr_api_key = description.api_key

    def __str__(self):
        return f"<GrowattSensor {self.api_key}>"

    @property
    def native_value(self):
        """

        :return:
        """
        val = self.value
        if self.entity_description.precision is not None:
            val = round(val, self.entity_description.precision)
        return val

    @property
    def name(self) -> str | None:
        """Return the name of the entity.

        :return:
        """
        if hasattr(self, "_attr_name"):
            return self._attr_name
        if hasattr(self, "entity_description"):
            return self.entity_description.name
        return None

    @property
    def device_class(self) -> str | None:
        """Return the class of this device, from component DEVICE_CLASSES.

        :return:
        """
        if hasattr(self, "_attr_device_class"):
            return self._attr_device_class
        if hasattr(self, "entity_description"):
            return self.entity_description.device_class
        return None

    @property
    def api_key(self):
        if hasattr(self, '_attr_api_key'):
            return self._attr_api_key
        if hasattr(self, 'entity_description'):
            return self.entity_description.api_key
        return None


class GrowattTotal:

    def __init__(self, plant_info: PlantInfo):
        """

        :param plant_info:
        """

        self._attr_info_plant = plant_info

        self.totals = []

    def __str__(self):
        return f"<GrowattTotal {self.plant_name}[{self.plant_id}]>"

    @property
    def plant_id(self):
        return self._attr_info_plant.plantId

    @property
    def plant_name(self):
        return self._attr_info_plant.plantName

    def add_sensor(self, data, description):
        """

        :param data:
        :param description:
        :return:
        """

        self.totals.append(GrowattSensor(data, description))


class GrowattAppliance:
    def __init__(self, info_inverter: InverterInfo = None):
        """

        :param info_inverter:
        """
        self._attr_info_inverter: InverterInfo | None = info_inverter

        self.sensors = []

    def __str__(self):
        return f"<GrowattAppliance SN:{self.serial_number}[{self.device_alias}] " \
               f"Plant Name: {self.plant_name}[{self.plant_id}]>"

    @property
    def serial_number(self):
        return self._attr_info_inverter.device.get('deviceSn')

    @property
    def device_alias(self):
        return self._attr_info_inverter.device.get('deviceAilas')

    @property
    def plant_id(self):
        return self._attr_info_inverter.plant_info.plantId

    @property
    def plant_name(self):
        return self._attr_info_inverter.plant_info.plantName

    @property
    def get_device_info(self) -> dict:
        """

        :return:
        """
        inverter_info = self._attr_info_inverter

        return inverter_info.device

    def add_sensor(self, data, description):
        """

        :param data:
        :param description:
        :return:
        """

        self.sensors.append(GrowattSensor(data, description))

    def get_sensor(self, api_key) -> GrowattSensor | None:

        for sensor in self.sensors:
            if api_key == sensor.api_key:
                return sensor
        return None


class GrowattData:
    def __init__(self, api, username, password, device_id, growatt_type):
        """Init the growatt probe

        :param api:
        :param username:
        :param password:
        :param device_id:
        :param growatt_type:
        """

        self.growatt_type = growatt_type
        self.api = api
        self.device_id = device_id
        self.plant_id = None
        self.data = {}
        self.username = username
        self.password = password

    # @Throttle(SCAN_INTERVAL)
    def update(self):
        """Update probe data.

        :return:
        """

        self.api.login(self.username, self.password)
        logger.debug(f"Update data for {self.device_id} {self.growatt_type}")

        try:
            match self.growatt_type:
                case "total":
                    total_info = self.api.plant_info(self.device_id)
                    del total_info["deviceList"]
                    # PlantMoneyText comes in as "3.1/€" split between value and currency
                    plant_money_text, currency = total_info["plantMoneyText"].split("/")
                    total_info["plantMoneyText"] = plant_money_text
                    total_info["currency"] = currency
                    self.data = total_info
                case "inverter":
                    inverter_info = self.api.inverter_detail(self.device_id)
                    self.data = inverter_info
                case "tlx":
                    tlx_info = self.api.tlx_detail(self.device_id)
                    self.data = tlx_info["data"]
                case "storage":
                    storage_params = self.api.storage_params(self.device_id)

                    storage_bean = storage_params["storageBean"]
                    storage_params.pop('storageBean')

                    storage_detail_bean = storage_params["storageDetailBean"]
                    storage_params.pop('storageDetailBean')

                    storage_energy_overview = self.api.storage_energy_overview(
                        self.plant_id, self.device_id
                    )
                    self.data = {
                        **storage_bean,
                        **storage_detail_bean,
                        **storage_params,
                        **storage_energy_overview,
                    }
                case "mix":
                    mix_info = self.api.mix_info(self.device_id)
                    mix_totals = self.api.mix_totals(self.device_id, self.plant_id)
                    mix_system_status = self.api.mix_system_status(self.device_id, self.plant_id)

                    mix_detail = self.api.mix_detail(self.device_id, self.plant_id)
                    # Get the chart data and work out the time of the last entry, use this as the last time data was
                    # published to the Growatt Server
                    mix_chart_entries = mix_detail["chartData"]
                    sorted_keys = sorted(mix_chart_entries)

                    # Create datetime from the latest entry
                    date_now = dt.now().date()
                    last_updated_time = dt.parse_time(str(sorted_keys[-1]))
                    mix_detail["lastdataupdate"] = datetime.datetime.combine(
                        date_now, last_updated_time, dt.DEFAULT_TIME_ZONE
                    )

                    # Dashboard data is largely inaccurate for mix system but it is the only call with the ability to
                    # return the combined imported from grid value that is the combination of charging AND load
                    # consumption
                    dashboard_data = self.api.dashboard_data(self.plant_id)
                    # Dashboard values have units e.g. "kWh" as part of their returned string, so we remove it
                    dashboard_values_for_mix = {
                        # etouser is already used by the results from 'mix_detail' so we rebrand it as
                        # 'etouser_combined'
                        "etouser_combined": float(dashboard_data["etouser"].replace("kWh", ""))
                    }
                    self.data = {
                        **mix_info,
                        **mix_totals,
                        **mix_system_status,
                        **mix_detail,
                        **dashboard_values_for_mix,
                    }
        except json.decoder.JSONDecodeError as e:
            logger.error("Unable to fetch data from Growatt server")

    def get_data(self, variable):
        """Get the data.

        :param variable:
        :return:
        """
        return self.data.get(variable)

