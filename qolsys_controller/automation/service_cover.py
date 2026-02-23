import logging
from abc import abstractmethod
from typing import TYPE_CHECKING

from qolsys_controller.automation.service import AutomationService

if TYPE_CHECKING:
    from qolsys_controller.automation.device import QolsysAutomationDevice

LOGGER = logging.getLogger(__name__)


class CoverService(AutomationService):
    def __init__(self, automation_device: "QolsysAutomationDevice", endpoint: int = 0) -> None:
        super().__init__(automation_device=automation_device, endpoint=endpoint)
        self._service_name = "CoverService"
        self._current_position: int | None = None
        self._is_closed: bool = False

    @abstractmethod
    async def open(self) -> None:
        pass

    @abstractmethod
    async def close(self) -> None:
        pass

    @abstractmethod
    async def stop(self) -> None:
        pass

    @abstractmethod
    async def set_current_position(self) -> None:
        pass

    @abstractmethod
    def supports_open(self) -> bool:
        pass

    @abstractmethod
    def supports_close(self) -> bool:
        pass

    @abstractmethod
    def supports_stop(self) -> bool:
        pass

    @abstractmethod
    def supports_position(self) -> bool:
        pass

    @property
    def current_position(self) -> int | None:
        return self._current_position

    @current_position.setter
    def current_position(self, value: int) -> None:
        if not (0 <= value <= 99):
            LOGGER.error("%s - level: invalid value: %s", self.prefix, value)
            self._current_position = None
            return

        if self._current_position != value:
            self._current_position = value
            self.automation_device.notify()
            LOGGER.debug("%s - current_position: %s", self.prefix, value)

    @property
    def is_closed(self) -> bool:
        return self._is_closed

    @is_closed.setter
    def is_closed(self, value: bool) -> None:
        if self._is_closed != value:
            self._is_closed = value
            self.automation_device.notify()
            LOGGER.debug("%s - is_closed: %s", self.prefix, value)

    def info(self) -> list[str]:
        str = []
        str.append(f"{self.prefix} - is_closed: {self.is_closed}")
        str.append(f"{self.prefix} - current_position: {self.current_position}")
        str.append(f"{self.prefix} - supports_open: {self.supports_open()}")
        str.append(f"{self.prefix} - supports_close: {self.supports_close()}")
        str.append(f"{self.prefix} - supports_stop: {self.supports_stop()}")
        str.append(f"{self.prefix} - supports_position: {self.supports_position()}")
        return str
