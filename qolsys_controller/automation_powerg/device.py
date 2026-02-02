import logging
from typing import TYPE_CHECKING

from qolsys_controller.automation.device import QolsysAutomationDevice

if TYPE_CHECKING:
    from qolsys_controller.controller import QolsysController

LOGGER = logging.getLogger(__name__)


class QolsysAutomationDevicePowerG(QolsysAutomationDevice):
    def __init__(self, controller: "QolsysController", dict: dict[str, str]) -> None:
        super().__init__(controller, dict)

        self._short_device_id: str = ""

        # Add Status Service
        self.service_add_status_service(endpoint=0)

        super().update_automation_services()

    def update_power_device(self, data: dict[str, str]) -> None:
        pass

    # -----------------------------
    # properties + setters
    # -----------------------------

    @property
    def short_device_id(self) -> str:
        return self._short_device_id

    @short_device_id.setter
    def short_device_id(self, value: str) -> None:
        if value != self._short_device_id:
            self._short_device_id = value
            self.notify()
