import json
import logging
from typing import TYPE_CHECKING

from .adc_service import QolsysAdcService
from .adc_service_garagedoor import QolsysAdcGarageDoorService
from .enum_adc import vdFuncLocalControl, vdFuncName, vdFuncState, vdFuncType
from .observable import QolsysObservable

if TYPE_CHECKING:
    from .adc_service import QolsysAdcService

LOGGER = logging.getLogger(__name__)


class QolsysAdcDevice(QolsysObservable):
    def __init__(self, adc_dict: dict[str, str]) -> None:
        super().__init__()

        self._services: list[QolsysAdcService] = []

        self._id: str = adc_dict.get("_id", "")
        self._partition_id: str = adc_dict.get("partition_id", "")
        self._device_id: str = adc_dict.get("device_id", "")
        self._name: str = adc_dict.get("name", "")
        self._type: str = adc_dict.get("type", "")
        self._create_time: str = adc_dict.get("create_time", "")
        self._created_by: str = adc_dict.get("created_by", "")
        self._update_time: str = adc_dict.get("update_time", "")
        self._updated_by: str = adc_dict.get("updated_by", "")
        self._device_zone_list: str = adc_dict.get("device_zone_list", "")
        self._func_list = ""
        self.func_list = adc_dict.get("func_list", "")

    def update_adc_device(self, data: dict[str, str]) -> None:
        # Check if we are updating same device_id
        device_id_update = data.get("device_id", "")
        if device_id_update != self._device_id:
            LOGGER.error(
                "Updating ADC%s (%s) with ADC%s (different device_id)",
                self._device_id,
                self._name,
                device_id_update,
            )
            return

        self.start_batch_update()

        if "partition_id" in data:
            self.partition_id = data.get("partition_id", "")

        if "name" in data:
            self.name = data.get("name", "")

        if "type" in data:
            self.type = data.get("type", "")

        self.end_batch_update()

        if "func_list" in data:
            self.func_list = data.get("func_list", "")

    def get_adc_service(self, id: int) -> QolsysAdcService | None:
        for service in self._services:
            if service.id == id:
                return service
        return None

    def add_adc_service(
        self,
        id: int,
        local_control: vdFuncLocalControl,
        func_name: vdFuncName,
        func_type: vdFuncType,
        func_state: vdFuncState,
        timestamp: str,
    ) -> None:
        # Garage Door
        if func_name == vdFuncName.OPEN_CLOSE and func_type == vdFuncType.BINARY_ACTUATOR:
            LOGGER.debug("ADC%s (%s) - Adding garage door service", self.device_id, self.name)
            self._services.append(
                QolsysAdcGarageDoorService(self, id, func_name, local_control, func_type, func_state, timestamp)
            )
            self.notify()
            return

        # Add generic service if other services have beed identified
        LOGGER.debug("ADC%s (%s) - Adding generic service", self.device_id, self.name)
        self._services.append(QolsysAdcService(self, id, func_name, local_control, func_type, func_state, timestamp))
        self.notify()
        return

    # -----------------------------
    # properties + setters
    # -----------------------------

    @property
    def device_id(self) -> str:
        return self._device_id

    @device_id.setter
    def device_id(self, value: str) -> None:
        self._device_id = value

    @property
    def services(self) -> list[QolsysAdcService]:
        return self._services

    @property
    def partition_id(self) -> str:
        return self._partition_id

    @partition_id.setter
    def partition_id(self, value: str) -> None:
        if self._partition_id != value:
            LOGGER.debug("ADC%s (%s) - partition_id: %s", self.device_id, self.name, value)
            self._partition_id = value
            self.notify()

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if self._name != value:
            LOGGER.debug("ADC%s (%s) - name: %s", self.device_id, self.name, value)
            self._name = value
            self.notify()

    @property
    def type(self) -> str:
        return self._type

    @type.setter
    def type(self, value: str) -> None:
        if self._type != value:
            LOGGER.debug("ADC%s (%s) - type: %s", self.device_id, self.name, value)
            self._type = value
            self.notify()

    @property
    def func_list(self) -> str:
        return self._func_list

    @func_list.setter
    def func_list(self, value: str) -> None:
        if self._func_list != value:
            LOGGER.debug("ADC%s (%s) - func_list: %s", self.device_id, self.name, value)
            self._func_list = value

            try:
                json_func_list = json.loads(self._func_list)
                new_service_id: list[int] = []
                self.start_batch_update()

                for function in json_func_list:
                    try:
                        id = function.get("vdFuncId")
                        local_control = vdFuncLocalControl(function.get("vdFuncLocalControl"))
                        func_name = vdFuncName(function.get("vdFuncName"))
                        func_type = vdFuncType(function.get("vdFuncType"))
                        func_state = vdFuncState(function.get("vdFuncState"))
                        timestamp = function.get("vdFuncBackendTimestamp")
                        new_service_id.append(id)

                        service = self.get_adc_service(id)
                        if service is not None:
                            service.update_adc_service(func_name, local_control, func_type, func_state, timestamp)

                        if service is None:
                            self.add_adc_service(id, local_control, func_name, func_type, func_state, timestamp)

                    except ValueError as e:
                        LOGGER.error("Error converting value:", e)
                        continue

                # Check if service have been removed
                for service in self._services:
                    if service.id not in new_service_id:
                        self._services.remove(service)
                        self.notify()

                self.end_batch_update()

            except json.JSONDecodeError as e:
                LOGGER.error("ADC%s - Error parsing JSON:", self.device_id, e)

    def to_dict_adc(self) -> dict[str, str]:
        return {
            "_id": self._id,
            "partition_id": self.partition_id,
            "device_id": self.device_id,
            "name": self.name,
            "type": self.type,
            "func_list": self.func_list,
            "create_time": self._create_time,
            "created_by": self._created_by,
            "update_time": self._update_time,
            "updated_by": self._updated_by,
            "device_zone_list": self._device_zone_list,
        }
