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
    def is_battery_low_supported(self) -> bool:
        pass

    @abstractmethod
    def is_battery_level_supported(self) -> bool:
        pass

    def battery_level_value(self) -> int | None:
        return self._battery_level

    @property
    def battery_level(self) -> int | None:
        return self._battery_level

    @battery_level.setter
    def battery_level(self, value: int) -> None:
        if not self.is_battery_level_supported():
            self._level = None
            return

        if not (0 <= value <= 100):
            LOGGER.error(
                "%s[%s] BatteryService - battery_level: invalid value: %s",
                self.automation_device.prefix,
                self.endpoint,
                value,
            )
            self._level = None
            return

        if self._battery_level != value:
            self._battery_level = value
            self.automation_device.notify()
            LOGGER.debug(
                "%s[%s] BatteryService - battery_level: %s",
                self.automation_device.prefix,
                self.endpoint,
                self.battery_level,
            )

    @property
    def battery_low(self) -> bool:
        return self._battery_low

    @battery_low.setter
    def battery_low(self, value: bool) -> None:
        if not self.is_battery_low_supported():
            return

        if self._battery_low != value:
            self._battery_low = value
            self.automation_device.notify()
            LOGGER.debug(
                "%s[%s] BatteryService - battery_low: %s",
                self.automation_device.prefix,
                self.endpoint,
                self.battery_low,
            )

    def info(self) -> None:
        if self.is_battery_level_supported():
            LOGGER.debug(
                "%s[%s] BatteryService - battery_level: %s%%",
                self.automation_device.prefix,
                self.endpoint,
                self.battery_level,
            )
            return

        if self.is_battery_low_supported():
            LOGGER.debug(
                "%s[%s] BatteryService - low_battery: %s",
                self.automation_device.prefix,
                self.endpoint,
                self.battery_low,
            )
            return

        LOGGER.debug(
            "%s[%s] BatteryService - Disabled",
            self.automation_device.prefix,
            self.endpoint,
        )
