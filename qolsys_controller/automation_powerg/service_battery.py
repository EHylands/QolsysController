import logging
from typing import TYPE_CHECKING

from qolsys_controller.automation.service_battery import BatteryService

if TYPE_CHECKING:
    from qolsys_controller.automation.device import QolsysAutomationDevice


LOGGER = logging.getLogger(__name__)


class BatteryServicePowerG(BatteryService):
    def __init__(self, automation_device: "QolsysAutomationDevice", endpoint: int = 0) -> None:
        super().__init__(automation_device, endpoint)

    def is_battery_low_supported(self) -> bool:
        return False

    def is_battery_level_supported(self) -> bool:
        return False

    def update_automation_service(self) -> None:
        pass
