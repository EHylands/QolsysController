import logging
from abc import abstractmethod
from typing import TYPE_CHECKING

from qolsys_controller.automation.service import AutomationService

if TYPE_CHECKING:
    from qolsys_controller.automation.device import QolsysAutomationDevice

LOGGER = logging.getLogger(__name__)


class SirenService(AutomationService):
    def __init__(self, automation_device: "QolsysAutomationDevice", endpoint: int = 0) -> None:
        super().__init__(automation_device=automation_device, endpoint=endpoint)
        self._service_name = "SirenService"
        self._is_on: bool = False

    @abstractmethod
    async def turn_on(self) -> None:
        pass

    @abstractmethod
    async def turn_off(self) -> None:
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

    def info(self) -> list[str]:
        return [f"{self.prefix} - is_on: {self.is_on}"]
