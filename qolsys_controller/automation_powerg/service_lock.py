import logging
from typing import TYPE_CHECKING

from qolsys_controller.automation.service_lock import LockService

if TYPE_CHECKING:
    from qolsys_controller.automation.device import QolsysAutomationDevice


LOGGER = logging.getLogger(__name__)


class LockServicePowerG(LockService):
    def __init__(self, automation_device: "QolsysAutomationDevice", endpoint: int = 0) -> None:
        super().__init__(automation_device=automation_device, endpoint=endpoint)

    async def lock(self) -> None:
        if self.is_locked:
            LOGGER.debug(
                "%s[%s] LockServicePowerG - lock: already locked",
                self.automation_device.prefix,
                self.endpoint,
            )
            return

        self.is_locking = True
        self.is_unlocking = False
        self.automation_device.notify()
        self._is_locking = False  # Dont fire notify again, will update when status comes back
        await self.automation_device.controller.command_automation_door_lock(
            int(self.automation_device.virtual_node_id), self.endpoint
        )

    async def unlock(self) -> None:
        if not self.is_locked:
            LOGGER.debug(
                "%s[%s] LockServicePowerG - unlock: already unlocked",
                self.automation_device.prefix,
                self.endpoint,
            )
            return

        self.is_locking = False
        self.is_unlocking = True
        self.automation_device.notify()
        self._is_unlocking = False  # Dont fire notify again, will update when status comes back
        await self.automation_device.controller.command_automation_door_unlock(
            int(self.automation_device.virtual_node_id), self.endpoint
        )

    async def open(self) -> None:
        pass

    async def close(self) -> None:
        pass

    def is_lock_supported(self) -> bool:
        return True

    def is_open_supported(self) -> bool:
        return False

    def is_jam_supported(self) -> bool:
        return True

    def update_automation_service(self) -> None:
        self.is_locked = self.automation_device.status.lower() == "locked"
        self.jammed = self.automation_device.status.lower() == "jammed"
