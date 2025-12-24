import logging

from qolsys_controller.enum_zwave import ZwaveCommand

from .zwave_device import QolsysZWaveDevice

LOGGER = logging.getLogger(__name__)


class QolsysThermometer(QolsysZWaveDevice):
    def __init__(self, zwave_dict: dict[str, str]) -> None:
        super().__init__(zwave_dict)
        self._temprature_value = ""
        self._humidity_value = ""

    def update_raw(self, command: int, command_status: int, command_type: int, payload: list[int]) -> None:
        LOGGER.debug(
            "Raw Update (node%s) - command:%s status:%s type:%s payload:%s",
            self.node_id,
            command,
            command_status,
            command_type,
            payload,
        )

        if command == ZwaveCommand.SensorMultiLevel:
            LOGGER.debug("Received Thermometer sensor update")

    def to_dict_thermometer(self) -> dict[str, str]:
        return {
            "temperature_value": self._temprature_value,
            "humidity_value": self._humidity_value,
        }
