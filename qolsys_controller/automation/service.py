from abc import ABC
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from qolsys_controller.automation.device import QolsysAutomationDevice


class AutomationService(ABC):
    def __init__(self, automation_device: "QolsysAutomationDevice") -> None:
        self._automation_device = automation_device
        self._endpoint: int = 0

    @property
    def automation_device(self) -> "QolsysAutomationDevice":
        return self._automation_device

    @automation_device.setter
    def automation_device(self, value: "QolsysAutomationDevice") -> None:
        self._automation_device = value

    @property
    def endpoint(self) -> int:
        return self._endpoint

    @endpoint.setter
    def endpoint(self, value: int) -> None:
        self._endpoint = value
