import logging
from typing import TYPE_CHECKING, Any

from qolsys_controller.enum_zwave import ZwaveCommandClass

from .zwave_device import QolsysZWaveDevice

if TYPE_CHECKING:
    from .controller import QolsysController

LOGGER = logging.getLogger(__name__)


class QolsysExternalSiren(QolsysZWaveDevice):
    def __init__(self, controller: "QolsysController", zwave_dict: dict[str, str]) -> None:
        super().__init__(controller, zwave_dict)
        self._siren_status: bool = False

        if ZwaveCommandClass.SwitchBinary not in self.command_class_list:
            LOGGER.error("ExternalSiren - Invalid Command Class: %s", self.command_class_list)

    def is_on(self) -> bool:
        return self._siren_status

    async def turn_on(self) -> None:
        await self._controller.command_zwave_switch_binary_set(self.node_id, "0", True)

    async def turn_off(self) -> None:
        await self._controller.command_zwave_switch_binary_set(self.node_id, "0", False)

    def update_siren(self, data: dict[str, Any]) -> None:
        # Check if we are updating same node_id
        node_id_update = data.get("node_id", "")
        if node_id_update != self.node_id:
            LOGGER.error(
                "Updating ExternalSiren %s (%s) with ExternalSiren '%s' (different id)",
                self.node_id,
                self.node_name,
                node_id_update,
            )
            return

        self.start_batch_update()

        if "siren_status" in data:
            self.siren_status = data.get("siren_status", False)

        self.end_batch_update()

    def update_raw(self, payload: bytes) -> None:
        LOGGER.debug("Raw Update (node%s) - payload: %s", self.node_id, payload.hex())

        # Check length
        if len(payload) < 3:
            LOGGER.warning("Payload too short for Z-Wave External Siren Report: %s", payload.hex())
            return

        command_class, command, value = payload[:3]

        match command_class:
            case ZwaveCommandClass.SwitchBinary:
                if command == 0x03:
                    if value == 0xFF:
                        self.siren_status = True
                    elif value == 0x00:
                        self.siren_status = False
                    else:
                        LOGGER.warning("Unexpected Binary Switch value 0x%02X for node %s", value, self.node_id)

    def to_dict_external_siren(self) -> dict[str, Any]:
        return {"siren_status": self._siren_status, "node_id": self.node_id}

    # -----------------------------
    # properties + setters
    # -----------------------------

    @property
    def siren_status(self) -> bool:
        return self._siren_status

    @siren_status.setter
    def siren_status(self, value: bool) -> None:
        if self._siren_status != value:
            LOGGER.debug("ExternalSiren%s (%s) - siren_status: %s", self.node_id, self.node_name, value)
            self._siren_status = value
            self.notify()
