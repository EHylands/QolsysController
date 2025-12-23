import logging
from typing import TYPE_CHECKING

from .enum_adc import vdFuncLocalControl, vdFuncName, vdFuncState, vdFuncType

if TYPE_CHECKING:
    from .adc_device import QolsysAdcDevice

LOGGER = logging.getLogger(__name__)


class QolsysAdcService:
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
        super().__init__()
        self._parent_device: QolsysAdcDevice = parent_device
        self._id: int = id
        self._func_name: vdFuncName = func_name
        self._local_control: vdFuncLocalControl = local_control
        self._func_type: vdFuncType = func_type
        self._func_state: vdFuncState = func_state
        self._timestamp: str = timestamp

    def update_adc_service(
        self,
        func_name: vdFuncName,
        local_control: vdFuncLocalControl,
        func_type: vdFuncType,
        func_state: vdFuncState,
        timestamp: str,
    ) -> None:
        self.name = func_name
        self.local_control = local_control
        self.func_type = func_type
        self.func_state = func_state
        self.timestamp = timestamp

    # -----------------------------
    # properties + setters
    # -----------------------------

    @property
    def id(self) -> int:
        return self._id

    @property
    def func_name(self) -> vdFuncName:
        return self._func_name

    @func_name.setter
    def func_name(self, value: vdFuncName) -> None:
        if value != self._func_name:
            self._func_name = value
            LOGGER.debug(
                "ADC%s (%s) - Func%s - func_name:%s",
                self._parent_device.device_id,
                self._parent_device.name,
                self.id,
                self.func_name,
            )
            LOGGER.debug("Warning - Changing func_name will change device type - Not supported")
            self._parent_device.notify()

    @property
    def local_control(self) -> vdFuncLocalControl:
        return self._local_control

    @local_control.setter
    def local_control(self, value: vdFuncLocalControl) -> None:
        if value != self.local_control:
            self._local_control = value
            LOGGER.debug(
                "ADC%s (%s) - Func%s - local_control:%s",
                self._parent_device.device_id,
                self._parent_device.name,
                self.id,
                self.local_control,
            )
            self._parent_device.notify()

    @property
    def func_type(self) -> vdFuncType:
        return self._func_type

    @func_type.setter
    def func_type(self, value: vdFuncType) -> None:
        if value != self._func_type:
            self._func_type = value
            LOGGER.debug(
                "ADC%s (%s) - Func%s - func_type:%s",
                self._parent_device.device_id,
                self._parent_device.name,
                self.id,
                self.func_type,
            )
            LOGGER.debug("Warning - Changing func_type will change device type - Not supported")
            self._parent_device.notify()

    @property
    def func_state(self) -> vdFuncState:
        return self._func_state

    @func_state.setter
    def func_state(self, value: vdFuncState) -> None:
        if value != self._func_state:
            self._func_state = value
            LOGGER.debug(
                "ADC%s (%s) - Func%s - func_state:%s",
                self._parent_device.device_id,
                self._parent_device.name,
                self.id,
                self.func_state,
            )
            self._parent_device.notify()

    @property
    def timestamp(self) -> str:
        return self._timestamp

    @timestamp.setter
    def timestamp(self, value: str) -> None:
        if value != self._timestamp:
            self._timestamp = value
            LOGGER.debug(
                "ADC%s (%s) - Func%s - timestamp:%s",
                self._parent_device.device_id,
                self._parent_device.name,
                self.id,
                self.timestamp,
            )
            self._parent_device.notify()
