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
        self._service_name = "LockService"
        self._is_locked: bool = False
        self._is_locking: bool = False
        self._is_unlocking: bool = False
        self._is_open: bool = False
        self._is_openning: bool = False
        self._is_closing: bool = False
        self._is_jammed: bool = False

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
    def supports_lock(self) -> bool:
        pass

    @abstractmethod
    def supports_open(self) -> bool:
        pass

    @abstractmethod
    def supports_jam(self) -> bool:
        pass

    @property
    def is_locked(self) -> bool:
        return self._is_locked

    @is_locked.setter
    def is_locked(self, value: bool) -> None:
        # if self._is_locked != value:
        self._is_locked = value
        self.automation_device.notify()
        LOGGER.debug("%s - is_locked: %s", self.prefix, value)

    @property
    def is_locking(self) -> bool:
        return self._is_locking

    @is_locking.setter
    def is_locking(self, value: bool) -> None:
        if self._is_locking != value:
            self._is_locking = value
            self.automation_device.notify()
            LOGGER.debug("%s - is_locking: %s", self.prefix, value)

    @property
    def is_unlocking(self) -> bool:
        return self._is_unlocking

    @is_unlocking.setter
    def is_unlocking(self, value: bool) -> None:
        if self._is_unlocking != value:
            self._is_unlocking = value
            self.automation_device.notify()
            LOGGER.debug("%s - is_unlocking: %s", self.prefix, value)

    @property
    def is_open(self) -> bool:
        return self._is_open

    @is_open.setter
    def is_open(self, value: bool) -> None:
        if self._is_open != value:
            self._is_open = value
            self.automation_device.notify()
            LOGGER.debug("%s - is_open: %s", self.prefix, value)

    @property
    def is_openning(self) -> bool:
        return self._is_openning

    @is_openning.setter
    def is_openning(self, value: bool) -> None:
        if self._is_openning != value:
            self._is_openning = value
            self.automation_device.notify()
            LOGGER.debug("%s - is_openning: %s", self.prefix, value)

    @property
    def is_closing(self) -> bool:
        return self._is_closing

    @is_closing.setter
    def is_closing(self, value: bool) -> None:
        if self._is_closing != value:
            self._is_closing = value
            self.automation_device.notify()
            LOGGER.debug("%s - is_closing: %s", self.prefix, value)

    @property
    def is_jammed(self) -> bool:
        return self._is_jammed

    @is_jammed.setter
    def is_jammed(self, value: bool) -> None:
        if self._is_jammed != value:
            self._is_ammed = value
            self.automation_device.notify()
            LOGGER.debug("%s - is_jammed: %s", self.prefix, value)

    def info(self) -> None:
        LOGGER.debug("%s - supports_lock: %s", self.prefix, self.supports_lock())
        LOGGER.debug("%s - supports_open: %s", self.prefix, self.supports_open())
        LOGGER.debug("%s - supports_jam: %s", self.prefix, self.supports_jam())

        if self.supports_lock():
            LOGGER.debug("%s - is_locked: %s", self.prefix, self.is_locked)
        if self.supports_open():
            LOGGER.debug("%s - is_open: %s", self.prefix, self.is_open)
        if self.supports_jam():
            LOGGER.debug("%s - is_jammed: %s", self.prefix, self.is_jammed)
