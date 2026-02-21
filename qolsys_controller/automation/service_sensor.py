__all__ = ["SensorService"]

import logging
from typing import TYPE_CHECKING

from qolsys_controller.automation.service import AutomationService
from qolsys_controller.enum import QolsysEvent, QolsysSensorScale

if TYPE_CHECKING:
    from qolsys_controller.automation.device import QolsysAutomationDevice

LOGGER = logging.getLogger(__name__)


class QolsysSensor:
    def __init__(
        self,
        parent_device: "QolsysAutomationDevice",
        parent_service: "SensorService",
        unit: QolsysSensorScale,
    ) -> None:
        self._parent_device: QolsysAutomationDevice = parent_device
        self._parent_service: SensorService = parent_service
        self._value: float | None = None
        self._unit: QolsysSensorScale = unit

    @property
    def unit(self) -> QolsysSensorScale:
        return self._unit

    @property
    def value(self) -> float | None:
        return self._value

    @value.setter
    def value(self, new_value: float | None) -> None:
        if self._value != new_value:
            self._value = new_value
            LOGGER.debug("%s - value: %s (%s)", self._parent_service.prefix, new_value, self._unit.name)
            self._parent_device.notify()


class SensorService(AutomationService):
    def __init__(self, automation_device: "QolsysAutomationDevice", endpoint: int = 0) -> None:
        super().__init__(automation_device=automation_device, endpoint=endpoint)
        self._service_name = "SensorService"
        self._sensors: list[QolsysSensor] = []

    @property
    def sensors(self) -> list[QolsysSensor]:
        return self._sensors

    def sensor(self, unit: QolsysSensorScale) -> QolsysSensor | None:
        for sensor in self._sensors:
            if sensor.unit == unit:
                return sensor
        return None

    def sensor_add(self, new_sensor: QolsysSensor) -> None:
        for sensor in self._sensors:
            if sensor._unit == new_sensor._unit:
                LOGGER.error("Error Adding Sensor, unit allready present")
                return
        self._sensors.append(new_sensor)
        self._automation_device.notify()

        # Notify state
        self._automation_device._controller.state.state_observer.publish(
            QolsysEvent.EVENT_AUTDEV_SENSOR_ADD,
            node_id=self._automation_device.virtual_node_id,
            endpoint=self.endpoint,
            unit=new_sensor.unit,
        )

    def update_automation_service(self) -> None:
        pass

    def info(self) -> None:
        for sensor in self.sensors:
            LOGGER.debug("%s - Sensor: %s (%s)", self.prefix, sensor.value, sensor.unit.name)
