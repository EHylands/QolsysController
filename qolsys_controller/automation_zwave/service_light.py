import json
import logging
from json import JSONDecodeError
from typing import TYPE_CHECKING

from qolsys_controller.automation.service_light import LightService
from qolsys_controller.enum_zwave import ZwaveDeviceClass

if TYPE_CHECKING:
    from qolsys_controller.automation.device import QolsysAutomationDevice
    from qolsys_controller.automation_zwave.device import QolsysAutomationDeviceZwave


LOGGER = logging.getLogger(__name__)


class LightServiceZwave(LightService):
    def __init__(self, automation_device: "QolsysAutomationDevice", endpoint: int = 0) -> None:
        super().__init__(automation_device=automation_device, endpoint=endpoint)

    async def turn_on(self) -> None:
        if self.is_level_supported():
            await self.set_level(0xFF)  # Return to las known level
        else:
            await self.automation_device.controller.command_zwave_switch_binary_set(
                self.automation_device.virtual_node_id, str(self.endpoint), True
            )

    async def turn_off(self) -> None:
        if self.is_level_supported():
            await self.set_level(0)
        else:
            await self.automation_device.controller.command_zwave_switch_binary_set(
                self.automation_device.virtual_node_id, str(self.endpoint), False
            )

    async def set_level(self, level: int) -> None:
        await self.automation_device.controller.command_zwave_switch_multilevel_set(
            self.automation_device.virtual_node_id, str(self.endpoint), level
        )

    def is_level_supported(self) -> bool:
        if not isinstance(self.automation_device, QolsysAutomationDeviceZwave):
            LOGGER.error(
                "%s[%s] LightServiceZwave - Invalid Protocol",
                self.automation_device.prefix,
                self.endpoint,
            )
            return False

        if self.automation_device.generic_device_type in {
            ZwaveDeviceClass.SwitchMultilevel,
            ZwaveDeviceClass.RemoteSwitchMultilevel,
        }:
            return True

        if self.automation_device.generic_device_type in {ZwaveDeviceClass.SwitchBinary, ZwaveDeviceClass.RemoteSwitchBinary}:
            return False

        LOGGER.error(
            "AutDev%s [%s][%s][%s] LightServiceZwave - unknown generic device type for level support: %s",
            self.automation_device.virtual_node_id,
            self.automation_device.protocol,
            self.automation_device.virtual_node_id,
            self.endpoint,
            self.automation_device.generic_device_type,
        )

        return False

    def update_automation_service(self) -> None:
        try:
            dict = json.loads(self.automation_device.extras)
            self.level = int(dict.get("LEVEL", "0"))
            self.is_on = self.automation_device.status.lower() == "on"

        except (JSONDecodeError, ValueError, TypeError):
            LOGGER.error(
                "[%s] LightServiceZwave - update_automation_service - error parsing extras/status: %s / %s",
                self.automation_device.prefix,
                self.endpoint,
                self.automation_device.extras,
                self.automation_device.status,
            )
