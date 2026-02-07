import logging
from typing import TYPE_CHECKING

from qolsys_controller.automation.service_light import LightService
from qolsys_controller.enum_adc import vdFuncLocalControl, vdFuncName, vdFuncState, vdFuncType

if TYPE_CHECKING:
    from qolsys_controller.automation.device import QolsysAutomationDevice


LOGGER = logging.getLogger(__name__)


class LightServiceADC(LightService):
    def __init__(
        self,
        automation_device: "QolsysAutomationDevice",
        endpoint: int,
    ) -> None:
        super().__init__(automation_device=automation_device, endpoint=endpoint)

    async def turn_on(self) -> None:
        await self.automation_device.controller.command_panel_virtual_device_action(
            self.automation_device.virtual_node_id, self.endpoint, vdFuncState.ON
        )

    async def turn_off(self) -> None:
        await self.automation_device.controller.command_panel_virtual_device_action(
            self.automation_device.virtual_node_id, self.endpoint, vdFuncState.OFF
        )

    async def set_level(self, level: int) -> None:
        pass

    def supports_level(self) -> bool:
        return False

    def update_adc_service(
        self,
        local_control: vdFuncLocalControl,
        func_name: vdFuncName,
        func_type: vdFuncType,
        func_state: vdFuncState,
        timestamp: str,
    ) -> None:
        self.is_on = func_state == vdFuncState.ON

    def update_automation_service(self) -> None:
        pass
