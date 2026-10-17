from __future__ import annotations

import json
import logging
from json import JSONDecodeError
from typing import TYPE_CHECKING

from qolsys_controller.automation.service_light import LightService
from qolsys_controller.enum_zwave import ZwaveCommandClass

if TYPE_CHECKING:
    from qolsys_controller.automation.device import QolsysAutomationDevice


LOGGER = logging.getLogger(__name__)


class LightServiceZwave(LightService):
    def __init__(self, automation_device: QolsysAutomationDevice, endpoint: int = 0) -> None:
        super().__init__(automation_device=automation_device, endpoint=endpoint)

    async def turn_on(self) -> None:
        if self.supports_level():
            await self.set_level(0xFF)  # Return to last known level
        else:
            await self.automation_device.controller.commands.zwave.switch_binary_set(
                self.automation_device.virtual_node_id, str(self.endpoint), True
            )

    async def turn_off(self) -> None:
        if self.supports_level():
            await self.set_level(0)
        else:
            await self.automation_device.controller.commands.zwave.switch_binary_set(
                self.automation_device.virtual_node_id, str(self.endpoint), False
            )

    async def set_level(self, level: int) -> None:
        await self.automation_device.controller.commands.zwave.switch_multilevel_set(
            self.automation_device.virtual_node_id, str(self.endpoint), level
        )

    def supports_level(self) -> bool:
        from qolsys_controller.automation_zwave.device import QolsysAutomationDeviceZwave

        if isinstance(self.automation_device, QolsysAutomationDeviceZwave):
            return ZwaveCommandClass.SwitchMultilevel in self.automation_device.command_class_list
        LOGGER.error(
            "%s[%s] LightServiceZwave - supports_level - Error, not a QolsysAutomationDeviceZwave",
            self.automation_device.prefix,
            self.endpoint,
        )
        return False

    def update_automation_service(self) -> None:
        try:
            dict = json.loads(self.automation_device.extras)
            self.is_on = self.automation_device.status.lower() == "on"
            # extras["LEVEL"] holds the dimmer's last/return-to brightness, which the panel
            # keeps even while the light is off. The live SwitchMultilevel/Basic reports
            # (parse_command_26/parse_command_20) treat level as the instantaneous output
            # (0 when off), so only trust extras while on; otherwise this refresh clobbers
            # the reported 0 and the level visibly bounces (e.g. 60 -> 0 -> 60).
            self.level = int(dict.get("LEVEL", "0")) if self.is_on else 0

        except (JSONDecodeError, ValueError, TypeError):
            LOGGER.error(
                "[%s] LightServiceZwave - update_automation_service - error parsing extras: %s",
                self.automation_device.prefix,
                self.automation_device.extras,
            )
