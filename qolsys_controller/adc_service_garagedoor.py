import logging
from typing import TYPE_CHECKING

from .adc_service import QolsysAdcService
from .enum_adc import vdFuncLocalControl, vdFuncName, vdFuncState, vdFuncType

if TYPE_CHECKING:
    from .adc_device import QolsysAdcDevice

LOGGER = logging.getLogger(__name__)


class QolsysAdcGarageDoorService(QolsysAdcService):
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

    def is_open(self) -> bool:
        return self.func_state == vdFuncState.ON
