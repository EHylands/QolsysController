from typing import TYPE_CHECKING

from qolsys_controller.automation.service import AutomationService

if TYPE_CHECKING:
    from qolsys_controller.automation.device import QolsysAutomationDevice


class LockServicePowerG(AutomationService):
    def __init__(self, automation_device: "QolsysAutomationDevice") -> None:
        super().__init__(automation_device)
        self._is_locking = False
        self._is_unlocking = False

    def lock(self) -> None:
        self._is_locking = True
        self._is_unlocking = False
        self._automation_device.notify()
        # Logic to lock

    def unlock(self) -> None:
        self._is_locking = False
        self._is_unlocking = True
        self._automation_device.notify()
        # Logic to unlock

    def is_locked(self) -> bool:
        return self.automation_device.status.lower() == "locked"

    def is_locking(self) -> bool:
        return self._is_locking

    def is_unlocking(self) -> bool:
        return self._is_unlocking

    def is_jammed(self) -> bool:
        return False
