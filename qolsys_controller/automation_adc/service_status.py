import logging
from typing import TYPE_CHECKING

from qolsys_controller.automation.service_status import StatusService
from qolsys_controller.enum_adc import vdFuncLocalControl, vdFuncName, vdFuncState, vdFuncType

if TYPE_CHECKING:
    from qolsys_controller.automation.device import QolsysAutomationDevice


LOGGER = logging.getLogger(__name__)


class StatusServiceADC(StatusService):
    def __init__(
        self,
        automation_device: "QolsysAutomationDevice",
        endpoint: int,
    ) -> None:
        super().__init__(automation_device=automation_device, endpoint=endpoint)

    async def set_level(self, level: int) -> None:
        pass

    def supports_status(self) -> bool:
        return True

    def update_adc_service(
        self,
        local_control: vdFuncLocalControl,
        func_name: vdFuncName,
        func_type: vdFuncType,
        func_state: vdFuncState,
        timestamp: str,
    ) -> None:
        self.is_malfunctioning = func_state == vdFuncState.ON

    def update_automation_service(self) -> None:
        pass
