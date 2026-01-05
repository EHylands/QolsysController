__all__ = ["QolsysZwaveMultilevelSensor"]

import logging
from enum import IntEnum
from typing import TYPE_CHECKING, Any

from qolsys_controller.enum import QolsysEvent
from qolsys_controller.enum_zwave import ZWaveMultilevelSensorScale

if TYPE_CHECKING:
    from .zwave_device import QolsysZWaveDevice

LOGGER = logging.getLogger(__name__)


def get_enum_by_name(enum: type[IntEnum], name: str) -> IntEnum | None:
    for val in enum:
        if val.name.upper() == name.upper():
            return val
    return None


class QolsysZwaveMultilevelSensor:
    def __init__(
        self,
        parent_device: "QolsysZWaveDevice",
        parent_sensor: "QolsysZwaveServiceMultilevelSensor",
        unit: ZWaveMultilevelSensorScale,
    ) -> None:
        self._parent_device: QolsysZWaveDevice = parent_device
        self._parent_meter: QolsysZwaveServiceMultilevelSensor = parent_sensor
        self._value: float | None = None
        self._unit: ZWaveMultilevelSensorScale = unit

    @property
    def unit(self) -> ZWaveMultilevelSensorScale:
        return self._unit

    @property
    def value(self) -> float | None:
        return self._value

    @value.setter
    def value(self, new_value: float | None) -> None:
        if self._value != new_value:
            self._value = new_value
            LOGGER.debug(
                "ZWaveMultilevelSensor%s-%s (%s) - value: %s (%s)",
                self._parent_device.node_id,
                self._parent_meter.endpoint,
                self._parent_device.node_name,
                new_value,
                self._unit.name,
            )
            self._parent_device.notify()


class QolsysZwaveServiceMultilevelSensor:
    def __init__(self, parent_device: "QolsysZWaveDevice", endpoint: str, sensor_dict: dict[str, Any]) -> None:
        self._parent_device: QolsysZWaveDevice = parent_device
        self._endpoint: str = endpoint
        self._sensors: list[QolsysZwaveMultilevelSensor] = []

        # Update sensor values
        self.update_iq2medi(sensor_dict)

    @property
    def sensors(self) -> list[QolsysZwaveMultilevelSensor]:
        return self._sensors

    def add_sensor(self, new_sensor: QolsysZwaveMultilevelSensor) -> None:
        for sensor in self._sensors:
            if sensor._unit == new_sensor._unit:
                LOGGER.error("Error Adding Sensor, unit allready present")
                return
        self._sensors.append(new_sensor)
        self._parent_device.notify()

        # Notify state
        self._parent_device._controller.state.state_observer.publish(
            QolsysEvent.EVENT_ZWAVE_MULTILEVELSENSOR_ADD,
            node_id=self._parent_device.node_id,
            endpoint=self.endpoint,
            unit=new_sensor.unit,
        )

    def get_sensor(self, unit: ZWaveMultilevelSensorScale) -> QolsysZwaveMultilevelSensor | None:
        for sensor in self._sensors:
            if sensor.unit == unit:
                return sensor
        return None

    @property
    def endpoint(self) -> str:
        return self._endpoint

    def update_iq2medi(self, data: dict[str, Any]) -> None:
        # Update Z-Wave Multilevelsensor Service

        self._parent_device.start_batch_update()

        # Update Sensors Values
        for key, value in data.items():
            if key == "AIR TEMPERATURE":
                temperature: float | None = value.get("Fahrenheit (F)", None)
                sensor = self.get_sensor(ZWaveMultilevelSensorScale.TEMPERATURE_FAHRENHEIT)
                if sensor:
                    sensor.value = temperature
                else:
                    sensor = QolsysZwaveMultilevelSensor(
                        self._parent_device, self, ZWaveMultilevelSensorScale.TEMPERATURE_FAHRENHEIT
                    )
                    self.add_sensor(sensor)
                    sensor.value = temperature

            if key == "HUMIDITY":
                humidity: float | None = value.get("Percentage value (%)", None)
                sensor = self.get_sensor(ZWaveMultilevelSensorScale.RELATIVE_HUMIDITY)
                if sensor:
                    sensor.value = humidity
                else:
                    sensor = QolsysZwaveMultilevelSensor(
                        self._parent_device, self, ZWaveMultilevelSensorScale.RELATIVE_HUMIDITY
                    )
                    self.add_sensor(sensor)
                    sensor.value = humidity

        self._parent_device.end_batch_update()
