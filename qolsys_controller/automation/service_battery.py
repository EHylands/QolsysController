from abc import abstractmethod
from typing import TYPE_CHECKING

from qolsys_controller.automation.service import AutomationService

if TYPE_CHECKING:
    from qolsys_controller.automation.device import QolsysAutomationDevice


class BatteryService(AutomationService):
    def __init__(self, automation_device: "QolsysAutomationDevice") -> None:
        super().__init__(automation_device=automation_device)

    @abstractmethod
    def is_battery_enabled(self) -> bool:
        pass

    @abstractmethod
    def is_battery_level_value_enabled(self) -> bool:
        pass

    @abstractmethod
    def battery_level_value(self) -> int | None:
        pass

    @abstractmethod
    def low_battery(self) -> bool:
        pass
