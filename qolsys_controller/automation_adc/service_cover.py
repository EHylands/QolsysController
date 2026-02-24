import logging
from typing import TYPE_CHECKING

from qolsys_controller.automation.service_cover import CoverService
from qolsys_controller.enum_adc import vdFuncLocalControl, vdFuncName, vdFuncState, vdFuncType

if TYPE_CHECKING:
    from qolsys_controller.automation.device import QolsysAutomationDevice


LOGGER = logging.getLogger(__name__)


class CoverServiceADC(CoverService):
    def __init__(
        self,
        automation_device: "QolsysAutomationDevice",
        endpoint: int,
    ) -> None:
        super().__init__(automation_device=automation_device, endpoint=endpoint)
        self._func_type: vdFuncType = vdFuncType.UNKNOWN

    @property
    def func_type(self) -> vdFuncType:
        return self._func_type

    async def open(self) -> None:
        await self.automation_device.controller.command_panel_virtual_device_action(
            self.automation_device.virtual_node_id, self.endpoint, vdFuncState.ON
        )

    async def close(self) -> None:
        await self.automation_device.controller.command_panel_virtual_device_action(
            self.automation_device.virtual_node_id, self.endpoint, vdFuncState.OFF
        )

    async def stop(self) -> None:
        pass

    async def set_current_position(self) -> None:
        pass

    def supports_open(self) -> bool:
        return True

    def supports_close(self) -> bool:
        return True

    def supports_stop(self) -> bool:
        return False

    def supports_position(self) -> bool:
        return False

    def update_adc_service(
        self,
        local_control: vdFuncLocalControl,
        func_name: vdFuncName,
        func_type: vdFuncType,
        func_state: vdFuncState,
        timestamp: str,
    ) -> None:
        self.is_closed = func_state == vdFuncState.OFF
        self._func_type = func_type

    def update_automation_service(self) -> None:
        pass
