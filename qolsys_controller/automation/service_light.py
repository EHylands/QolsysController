import logging
from abc import abstractmethod
from typing import TYPE_CHECKING

from qolsys_controller.automation.service import AutomationService

if TYPE_CHECKING:
    from qolsys_controller.automation.device import QolsysAutomationDevice

LOGGER = logging.getLogger(__name__)


class LightService(AutomationService):
    def __init__(self, automation_device: "QolsysAutomationDevice", endpoint: int = 0) -> None:
        super().__init__(automation_device=automation_device, endpoint=endpoint)
        self._service_name = "LightService"
        self._level: int | None = None
        self._is_on: bool = False

    @abstractmethod
    async def turn_on(self) -> None:
        pass

    @abstractmethod
    async def turn_off(self) -> None:
        pass

    @abstractmethod
    async def set_level(self, level: int) -> None:
        pass

    @abstractmethod
    def supports_level(self) -> bool:
        pass

    @property
    def is_on(self) -> bool:
        return self._is_on

    @is_on.setter
    def is_on(self, value: bool) -> None:
        if self._is_on != value:
            self._is_on = value
            self.automation_device.notify()
            LOGGER.debug("%s - is_on: %s", self.prefix, value)

    @property
    def level(self) -> int | None:
        return self._level

    @level.setter
    def level(self, value: int) -> None:
        if not (0 <= value <= 99):
            LOGGER.error("%s[ - level: invalid value: %s", self.prefix, value)
            self._level = None
            return

        if self._level != value:
            self._level = value
            self.automation_device.notify()
            LOGGER.debug("%s - level: %s", self.prefix, value)

    def info(self) -> list[str]:
        str = []
        str.append(f"{self.prefix} - is_on: {self.is_on}")
        str.append(f"{self.prefix} - level: {self.level}")
        str.append(f"{self.prefix} - supports_level: {self.supports_level()}")
        return str
