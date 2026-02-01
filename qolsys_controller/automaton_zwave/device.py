import logging
from typing import TYPE_CHECKING

from qolsys_controller.automation.device import QolsysAutomationDevice

if TYPE_CHECKING:
    from qolsys_controller.controller import QolsysController

LOGGER = logging.getLogger(__name__)


class QolsysAutomationDeviceZwave(QolsysAutomationDevice):
    def __init__(self, controller: "QolsysController", dict: dict[str, str]) -> None:
        super().__init__(controller, dict)

        # Add Battery Service
        self.service_add_battery_service()

    def update_zwave_device(self, data: dict[str, str]) -> None:
        pass

    # -----------------------------
    # properties + setters
    # -----------------------------
