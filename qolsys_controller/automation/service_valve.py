import logging
from abc import abstractmethod
from typing import TYPE_CHECKING

from qolsys_controller.automation.service import AutomationService

if TYPE_CHECKING:
    from qolsys_controller.automation.device import QolsysAutomationDevice

LOGGER = logging.getLogger(__name__)


class ValveService(AutomationService):
    def __init__(self, automation_device: "QolsysAutomationDevice", endpoint: int = 0) -> None:
        super().__init__(automation_device=automation_device, endpoint=endpoint)
        self._service_name = "ValveService"
        self._is_closed: bool = False
        self._is_closing: bool = False
        self._is_opening: bool = False
        self._current_position: int | None = None

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
    async def set_position(self, position: int) -> None:
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
    def is_closed(self) -> bool:
        return self._is_closed

    @is_closed.setter
    def is_closed(self, value: bool) -> None:
        if self._is_closed != value:
            self._is_closed = value
            self.automation_device.notify()
            LOGGER.debug("%s - is_closed: %s", self.prefix, value)

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
    def is_opening(self) -> bool:
        return self._is_opening

    @is_opening.setter
    def is_opening(self, value: bool) -> None:
        if self._is_opening != value:
            self._is_opening = value
            self.automation_device.notify()
            LOGGER.debug("%s - is_opening: %s", self.prefix, value)

    @property
    def current_position(self) -> int | None:
        return self._current_position

    @current_position.setter
    def current_position(self, value: int) -> None:
        if not (0 <= value <= 100):
            LOGGER.error("%s - current_position: invalid value: %s", self.prefix, value)
            self._current_position = None
            return

        if self._current_position != value:
            self._current_position = value
            self.automation_device.notify()
            LOGGER.debug("%s - current_position: %s", self.prefix, value)

    def info(self) -> list[str]:
        lines = []
        lines.append(f"{self.prefix} - supports_open: {self.supports_open()}")
        lines.append(f"{self.prefix} - supports_close: {self.supports_close()}")
        lines.append(f"{self.prefix} - supports_stop: {self.supports_stop()}")
        lines.append(f"{self.prefix} - supports_position: {self.supports_position()}")
        lines.append(f"{self.prefix} - is_closed: {self.is_closed}")
        lines.append(f"{self.prefix} - is_closing: {self.is_closing}")
        lines.append(f"{self.prefix} - is_opening: {self.is_opening}")
        if self.supports_position():
            lines.append(f"{self.prefix} - current_position: {self.current_position}")
        return lines
