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
        self._service_name = "StatusService"
        self._is_malfunctioning: bool = False

    @abstractmethod
    def supports_status(self) -> bool:
        pass

    @property
    def is_malfunctioning(self) -> bool:
        return self._is_malfunctioning

    @is_malfunctioning.setter
    def is_malfunctioning(self, value: bool) -> None:
        if self._is_malfunctioning != value:
            self._is_malfunctioning = value
            self.automation_device.notify()
            LOGGER.debug(
                "%s[%s] StatusService - is_malfunctioning: %s",
                self.automation_device.prefix,
                self.endpoint,
                value,
            )

    def info(self) -> None:
        LOGGER.debug(
            "%s[%s] StatusService - is_malfunctioning: %s",
            self.automation_device.prefix,
            self.endpoint,
            self.is_malfunctioning,
        )
