import logging
from abc import abstractmethod
from typing import TYPE_CHECKING

from qolsys_controller.automation.service import AutomationService

if TYPE_CHECKING:
    from qolsys_controller.automation.device import QolsysAutomationDevice

LOGGER = logging.getLogger(__name__)


class StatusService(AutomationService):
    def __init__(self, automation_device: "QolsysAutomationDevice", endpoint: int = 0) -> None:
        super().__init__(automation_device=automation_device, endpoint=endpoint)

        self._malfunction: bool = False

    @abstractmethod
    def is_status_supported(self) -> bool:
        pass

    @property
    def malfunction(self) -> bool:
        return self._malfunction

    @malfunction.setter
    def malfunction(self, value: bool) -> None:
        if self._malfunction != value:
            self._malfunction = value
            self.automation_device.notify()
            LOGGER.debug(
                "%s[%s] StatusService - malfunction: %s",
                self.automation_device.prefix,
                self.endpoint,
                self.malfunction,
            )

    def info(self) -> None:
        LOGGER.debug(
            "%s[%s] StatusService - malfunction: %s",
            self.automation_device.prefix,
            self.endpoint,
            self.malfunction,
        )
