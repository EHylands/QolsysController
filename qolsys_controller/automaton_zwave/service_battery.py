from typing import TYPE_CHECKING

from qolsys_controller.automation.service_battery import BatteryService

if TYPE_CHECKING:
    from qolsys_controller.automation.device import QolsysAutomationDevice


class BatteryServiceZwave(BatteryService):
    def __init__(self, automation_device: "QolsysAutomationDevice") -> None:
        super().__init__(automation_device)

    def is_battery_enabled(self) -> bool:
        return False

    def is_battery_level_value_enabled(self) -> bool:
        return self.battery_level_value is not None

    def battery_level_value(self) -> int | None:
        try:
            value = int(self._automation_device._node_battery_level_value)
            if 0 <= value <= 100:
                return value
            return None
        except ValueError:
            return None

    def low_battery(self) -> bool:
        return False
