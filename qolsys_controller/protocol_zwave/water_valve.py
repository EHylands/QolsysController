import logging
from typing import TYPE_CHECKING, Any

from qolsys_controller.enum_zwave import ZwaveCommandClass
from qolsys_controller.protocol_zwave.device import QolsysZWaveDevice

if TYPE_CHECKING:
    from qolsys_controller.controller import QolsysController

LOGGER = logging.getLogger(__name__)


class QolsysWaterValve(QolsysZWaveDevice):
    def __init__(self, controller: "QolsysController", zwave_dict: dict[str, str]) -> None:
        super().__init__(controller, zwave_dict)
        self._valve_status: bool = False  # True open, False closed

        if ZwaveCommandClass.SwitchBinary not in self.command_class_list:
            LOGGER.error("Water Valve - Invalid Command Class: %s", self.command_class_list)

    def is_closed(self) -> bool:
        return not self.valve_status

    async def close_valve(self) -> None:
        await self._controller.command_zwave_switch_binary_set(self.node_id, self.endpoint, False)

    async def open_valve(self) -> None:
        await self._controller.command_zwave_switch_binary_set(self.node_id, self.endpoint, True)

    def update_valve(self, data: dict[str, Any]) -> None:
        # Check if we are updating same node_id
        node_id_update = data.get("node_id", "")
        if node_id_update != self.node_id:
            LOGGER.error(
                "Updating WaterValve %s (%s) with WaterValve '%s' (different id)", self.node_id, self.node_name, node_id_update
            )
            return

        self.start_batch_update()

        if "valve_status" in data:
            self.valve_status = data.get("valve_status", False)

        self.end_batch_update()

    def update_raw(self, payload: bytes, endpoint: int = 0) -> None:
        super().update_raw(payload, endpoint)

        # Check length
        if len(payload) < 3:
            LOGGER.warning("Payload too short for Z-Wave Valve Report: %s", payload.hex())
            return

        command_class, command, value = payload[:3]

        match command_class:
            case ZwaveCommandClass.SwitchBinary:
                if command == 0x03:
                    if value == 0xFF:
                        self.valve_status = True
                    elif value == 0x00:
                        self.valve_status = False
                    else:
                        LOGGER.warning("Unexpected Binary Switch value 0x%02X for node %s", value, self.node_id)

    def to_dict_water_valve(self) -> dict[str, Any]:
        return {"valve_status": self._valve_status, "node_id": self.node_id}

    # -----------------------------
    # properties + setters
    # -----------------------------

    @property
    def valve_status(self) -> bool:
        return self._valve_status

    @valve_status.setter
    def valve_status(self, value: bool) -> None:
        if self._valve_status != value:
            LOGGER.debug("WaterValve%s (%s) - valve_status: %s", self.node_id, self.node_name, value)
            self._valve_status = value
            self.notify()
