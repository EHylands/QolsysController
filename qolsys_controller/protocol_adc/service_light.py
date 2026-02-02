import logging
from typing import TYPE_CHECKING

from qolsys_controller.enum_adc import vdFuncLocalControl, vdFuncName, vdFuncState, vdFuncType

from .service import QolsysAdcService

if TYPE_CHECKING:
    from .device import QolsysAdcDevice

LOGGER = logging.getLogger(__name__)


class QolsysAdcLightService(QolsysAdcService):
    def __init__(
        self,
        parent_device: "QolsysAdcDevice",
        id: int,
        func_name: vdFuncName,
        local_control: vdFuncLocalControl,
        func_type: vdFuncType,
        func_state: vdFuncState,
        timestamp: str,
    ) -> None:
        super().__init__(
            parent_device,
            id,
            func_name,
            local_control,
            func_type,
            func_state,
            timestamp,
        )

    def is_on(self) -> bool:
        return self.func_state == vdFuncState.ON
