#  -*- coding: utf-8 -*-

from dataclasses import dataclass

from RoundBox.core.hass.components.sensor import SensorEntityDescription


@dataclass
class GrowattRequiredKeysMixin:
    """Mixin for required keys."""

    api_key: str


@dataclass
class GrowattSensorEntityDescription(SensorEntityDescription, GrowattRequiredKeysMixin):
    """Describes Growatt sensor entity."""

    precision: int | None = None
    currency: bool = False
