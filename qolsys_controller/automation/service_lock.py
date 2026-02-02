import logging
from abc import abstractmethod
from typing import TYPE_CHECKING

from qolsys_controller.automation.service import AutomationService

if TYPE_CHECKING:
    from qolsys_controller.automation.device import QolsysAutomationDevice

LOGGER = logging.getLogger(__name__)


class LockService(AutomationService):
    def __init__(self, automation_device: "QolsysAutomationDevice", endpoint: int = 0) -> None:
        super().__init__(automation_device=automation_device, endpoint=endpoint)

        self._is_lock_supported: bool = False
        self._is_open_supported: bool = False
        self._is_jam_supported: bool = False

        self._locked: bool = False
        self._locking: bool = False
        self._unlocking: bool = False

        self._openned: bool = False
        self._openning: bool = False
        self._closing: bool = False

        self._jammed: bool = False

    @abstractmethod
    async def lock(self) -> None:
        pass

    @abstractmethod
    async def unlock(self) -> None:
        pass

    @abstractmethod
    async def open(self) -> None:
        pass

    @abstractmethod
    async def close(self) -> None:
        pass

    @abstractmethod
    def is_lock_supported(self) -> bool:
        pass

    @abstractmethod
    def is_open_supported(self) -> bool:
        pass

    @abstractmethod
    def is_jam_supported(self) -> bool:
        pass

    @property
    def locked(self) -> bool:
        return self._locked

    @locked.setter
    def locked(self, value: bool) -> None:
        if self._locked != value:
            self._locked = value
            self.automation_device.notify()
            LOGGER.debug(
                "%s[%s] LockService - locked: %s",
                self.automation_device.prefix,
                self.endpoint,
                self.locked,
            )

    @property
    def locking(self) -> bool:
        return self._locking

    @locking.setter
    def locking(self, value: bool) -> None:
        if self._locking != value:
            self._locking = value
            self.automation_device.notify()
            LOGGER.debug(
                "%s[%s] LockService - locking: %s",
                self.automation_device.prefix,
                self.endpoint,
                self.locking,
            )

    @property
    def unlocking(self) -> bool:
        return self._unlocking

    @unlocking.setter
    def unlocking(self, value: bool) -> None:
        if self._unlocking != value:
            self._unlocking = value
            self.automation_device.notify()
            LOGGER.debug(
                "%s[%s] LockService - unlocking: %s",
                self.automation_device.prefix,
                self.endpoint,
                self.unlocking,
            )

    @property
    def openned(self) -> bool:
        return self._openned

    @openned.setter
    def openned(self, value: bool) -> None:
        if self._openned != value:
            self._openned = value
            self.automation_device.notify()
            LOGGER.debug(
                "%s[%s] LockService - openned: %s",
                self.automation_device.prefix,
                self.endpoint,
                self.openned,
            )

    @property
    def openning(self) -> bool:
        return self._openning

    @openning.setter
    def openning(self, value: bool) -> None:
        if self._openning != value:
            self._openning = value
            self.automation_device.notify()
            LOGGER.debug(
                "%s[%s] LockService - openning: %s",
                self.automation_device.prefix,
                self.endpoint,
                self.openning,
            )

    @property
    def closing(self) -> bool:
        return self._closing

    @closing.setter
    def closing(self, value: bool) -> None:
        if self._closing != value:
            self._closing = value
            self.automation_device.notify()
            LOGGER.debug(
                "%s[%s] LockService - closing: %s",
                self.automation_device.prefix,
                self.endpoint,
                self.closing,
            )

    @property
    def jammed(self) -> bool:
        return self._jammed

    @jammed.setter
    def jammed(self, value: bool) -> None:
        if self._jammed != value:
            self._jammed = value
            self.automation_device.notify()
            LOGGER.debug(
                "%s[%s] LockService - jammed: %s",
                self.automation_device.prefix,
                self.endpoint,
                self.jammed,
            )

    def info(self) -> None:
        if self.is_lock_supported():
            LOGGER.debug(
                "%s[%s] LockService - locked: %s",
                self.automation_device.prefix,
                self.endpoint,
                self.locked,
            )
        if self.is_open_supported():
            LOGGER.debug(
                "%s[%s] LockService - openned: %s",
                self.automation_device.prefix,
                self.endpoint,
                self.openned,
            )
        if self.is_jam_supported():
            LOGGER.debug(
                "%s[%s] LockService - jammed: %s",
                self.automation_device.prefix,
                self.endpoint,
                self.jammed,
            )
