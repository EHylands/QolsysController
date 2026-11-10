from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from qolsys_controller.automation.service_valve import ValveService
from qolsys_controller.enum_qolsys import QolsysNotification
from qolsys_controller.enum_zwave import ZwaveCommandClass
from qolsys_controller.observable import Event

if TYPE_CHECKING:
    from qolsys_controller.automation.device import QolsysAutomationDevice

LOGGER = logging.getLogger(__name__)


class ValveServiceZwave(ValveService):
    def __init__(self, automation_device: QolsysAutomationDevice, endpoint: int = 0) -> None:
        super().__init__(automation_device=automation_device, endpoint=endpoint)

    async def open(self) -> None:

        if ZwaveCommandClass.SwitchBinary not in self.automation_device.command_class_list:  # type: ignore[attr-defined]
            LOGGER.error("%s - Valve does not support SwitchBinary command class", self.prefix)
            return

        self.is_closing = False
        self.is_opening = True
        self.automation_device.notify(
            Event(QolsysNotification.AUTOMATION_UPDATE, self.automation_device, self.automation_device.to_dict_event())
        )
        self._is_opening = False

        await self.automation_device.controller.commands.zwave.switch_binary_set(
            self.automation_device.virtual_node_id, str(self.endpoint), False
        )

    async def close(self) -> None:

        if ZwaveCommandClass.SwitchBinary not in self.automation_device.command_class_list:  # type: ignore[attr-defined]
            LOGGER.error("%s - Valve does not support SwitchBinary command class", self.prefix)
            return

        self.is_closing = True
        self.is_opening = False
        self.automation_device.notify(
            Event(QolsysNotification.AUTOMATION_UPDATE, self.automation_device, self.automation_device.to_dict_event())
        )
        self._is_closing = False

        await self.automation_device.controller.commands.zwave.switch_binary_set(
            self.automation_device.virtual_node_id, str(self.endpoint), True
        )

    async def stop(self) -> None:
        pass

    async def set_position(self, position: int) -> None:
        pass

    def supports_open(self) -> bool:
        return True

    def supports_close(self) -> bool:
        return True

    def supports_stop(self) -> bool:
        return False

    def supports_position(self) -> bool:
        return False

    def update_automation_service(self) -> None:
        LOGGER.debug(
            "%s - panel status: %r",
            self.prefix,
            self.automation_device.status,
        )

        status = self.automation_device.status.lower()
        if status in ("open", "close"):
            self.is_closed = status == "close"
        else:
            LOGGER.warning(
                "%s - Unexpected valve status %r, please report it at https://github.com/EHylands/QolsysController/issues",
                self.prefix,
                self.automation_device.status,
            )
