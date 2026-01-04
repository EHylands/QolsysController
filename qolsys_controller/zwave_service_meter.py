__all__ = ["QolsysZwaveMeterSensor"]

import json
import logging
from enum import IntEnum
from typing import TYPE_CHECKING, Any, Type

from qolsys_controller.enum_zwave import (
    MeterRateType,
    MeterType,
    ZWaveElectricMeterScale,
    ZWaveUnknownMeterScale,
)

if TYPE_CHECKING:
    from .zwave_device import QolsysZWaveDevice

LOGGER = logging.getLogger(__name__)


def get_enum_by_name(enum: type[IntEnum], name: str) -> IntEnum | None:
    for val in enum:
        if val.name.upper() == name.upper():
            return val
    return None


class QolsysZwaveMeterSensor:
    def __init__(self, parent_device: "QolsysZWaveDevice", parent_meter: "QolsysZwaveServiceMeter", scale: IntEnum) -> None:
        self._parent_device: QolsysZWaveDevice = parent_device
        self._parent_meter: QolsysZwaveServiceMeter = parent_meter
        self._scale: IntEnum = scale
        self._value: float | None = None
        self._delta_time: int | None = None
        self._previous_value: float | None = None

    @property
    def value(self) -> float | None:
        return self._value

    @value.setter
    def value(self, new_value: float | None) -> None:
        if self._value != new_value:
            self._value = new_value
            LOGGER.debug(
                "ZWaveMeter%s-%s (%s) - %s - value: %s (%s)",
                self._parent_device.node_id,
                self._parent_meter.endpoint,
                self._parent_device.node_name,
                self._parent_meter._meter_type.name,
                new_value,
                self._scale.name,
            )
            self._parent_device.notify()

    @property
    def scale(self) -> IntEnum:
        return self._scale


class QolsysZwaveServiceMeter:
    def __init__(self, parent_device: "QolsysZWaveDevice", endpoint: str, meter_dict: dict[str, Any]) -> None:
        self._parent_device: QolsysZWaveDevice = parent_device
        self._endpoint: str = endpoint
        self._meter_type: MeterType = MeterType.UNKNOWN
        self._rate_type: MeterRateType = MeterRateType.UNSPECIFIED
        self._scale_type: Type[IntEnum] = ZWaveUnknownMeterScale
        self._supported_scale: list[IntEnum] = []
        self._sensors: list[QolsysZwaveMeterSensor] = []
        self._master_reset_flag: bool = False

        # Set Meter_Type
        type: str | int = meter_dict.get("meter_type", "")
        if type == "ENERGY_METER" or type == MeterType.ELECTRIC_METER.value:
            self._meter_type = MeterType.ELECTRIC_METER
            self._scale_type = ZWaveElectricMeterScale
        else:
            LOGGER.warning("Zave Meter Service - Unknown Meter Type: %s", type)
            return

        # Set Rate Type
        rate_type: int = meter_dict.get("meter_ratetype_supported", -1)
        try:
            self._rate_type = MeterRateType(rate_type)
        except ValueError:
            LOGGER.error("Zave Meter Service - Unknown MeterRateType, Setting to UNSPECIFIED")
            self._rate_type = MeterRateType.UNSPECIFIED

        # Set Master Reset Flag
        self._master_reset_flag = bool(meter_dict.get("meter_master_reset_flag", False))

        # Set Supported Scales
        self.supported_scale = meter_dict.get("meter_scale_supported", "[]")

        # Create Sensors for Supported Scales
        for scale in self._supported_scale:
            qolsys_meter_sensor = QolsysZwaveMeterSensor(self._parent_device, self, scale)
            self.add_sensor(qolsys_meter_sensor)

        # Update sensor values
        self.update_iq2medi(meter_dict)

    @property
    def sensors(self) -> list[QolsysZwaveMeterSensor]:
        return self._sensors

    def add_sensor(self, new_sensor: QolsysZwaveMeterSensor) -> None:
        for sensor in self._sensors:
            if sensor._scale == new_sensor._scale:
                LOGGER.error("Error Adding Sensor, scale allready present")
                return
        self._sensors.append(new_sensor)
        self._parent_device.notify()

    def get_sensor(self, scale: IntEnum) -> QolsysZwaveMeterSensor | None:
        for sensor in self._sensors:
            if sensor._scale == scale:
                return sensor
        return None

    @property
    def endpoint(self) -> str:
        return self._endpoint

    @property
    def rate_type(self) -> MeterRateType:
        return self._rate_type

    @rate_type.setter
    def rate_type(self, value: MeterRateType) -> None:
        if self._rate_type != value:
            self._rate_type = value
            # LOGGER.debug("Zave Meter Service - rate_type: %s", value.name)
            self._parent_device.notify()

    @property
    def supported_scale(self) -> list[IntEnum]:
        return self._supported_scale

    @supported_scale.setter
    def supported_scale(self, value: str) -> None:
        try:
            scales = json.loads(value)
            cleaned = [s.strip() for s in scales]

        except json.JSONDecodeError:
            self._supported_scale = []
            LOGGER.error("Zave Meter Service - Error parsing meter_scale_supported, Setting to empty list")

        for key in cleaned:
            for scale in self._scale_type:
                if key.lower() == scale.name.lower():
                    if scale not in self._supported_scale:
                        self._supported_scale.append(scale)

    def update_iq2medi(self, data: dict[str, Any]) -> None:
        # Update Z-Wave Meter Service

        # Cannot change meter type once created
        type: str | int = data.get("meter_type", "")
        if type == "ENERGY_METER" or type == MeterType.ELECTRIC_METER:
            if self._meter_type is not MeterType.ELECTRIC_METER:
                LOGGER.error("Zave Meter Service - Cannot change Meter Type once created")
                return

        self._parent_device.start_batch_update()

        # Upate Rate Type
        if "meter_ratetype_supported" in data:
            rate_type: int = data.get("meter_ratetype_supported", -1)
            try:
                self.rate_type = MeterRateType(rate_type)
            except ValueError:
                LOGGER.error("Zave Meter Service - Unknown MeterRateType, Setting to UNSPECIFIED")
                self.rate_type = MeterRateType.UNSPECIFIED

        # Update Master Reset Flag
        if "meter_master_reset_flag" in data:
            self._master_reset_flag = bool(data.get("meter_master_reset_flag", False))

        # Update Meter Values
        if "meter_scale_reading_values" in data:
            scale_values: dict[str, Any] = data.get("meter_scale_reading_values", {})

            for key, value in scale_values.items():
                temp = get_enum_by_name(self._scale_type, key.strip())
                if temp in self._supported_scale:
                    sensor = self.get_sensor(temp)
                    if sensor is not None:
                        sensor.value = float(value)

        self._parent_device.end_batch_update()
