import logging
from abc import abstractmethod
from typing import TYPE_CHECKING

from qolsys_controller.automation.service import AutomationService

if TYPE_CHECKING:
    from qolsys_controller.automation.device import QolsysAutomationDevice

LOGGER = logging.getLogger(__name__)


class BatteryService(AutomationService):
    def __init__(self, automation_device: "QolsysAutomationDevice", endpoint: int = 0) -> None:
        super().__init__(automation_device=automation_device, endpoint=endpoint)
        self._service_name = "BatteryService"
        self._battery_level: int | None = None
        self._battery_low: bool = False

    @abstractmethod
    def supports_battery_low(self) -> bool:
        pass

    @abstractmethod
    def supports_battery_level(self) -> bool:
        pass

    @property
    def battery_level(self) -> int | None:
        return self._battery_level

    @battery_level.setter
    def battery_level(self, value: int) -> None:
        if not self.supports_battery_level():
            self._battery_level = None
            return

        if not (0 <= value <= 100):
            LOGGER.error("%s - battery_level: invalid value: %s", self.prefix, value)
            self._battery_level = None
            return

        if self._battery_level != value:
            self._battery_level = value
            self.automation_device.notify()
            LOGGER.debug("%s - battery_level: %s", self.prefix, value)

    @property
    def battery_low(self) -> bool:
        return self._battery_low

    @battery_low.setter
    def battery_low(self, value: bool) -> None:
        if not self.supports_battery_low():
            return

        if self._battery_low != value:
            self._battery_low = value
            self.automation_device.notify()
            LOGGER.debug("%s - battery_low: %s", self.prefix, value)

    def info(self) -> None:
        if self.supports_battery_level():
            LOGGER.debug("%s - battery_level: %s%%", self.prefix, self.battery_level)
            return

        if self.supports_battery_low():
            LOGGER.debug("%s - low_battery: %s", self.prefix, self.battery_low)
            return

        LOGGER.debug("%s - Disabled", self.prefix)
