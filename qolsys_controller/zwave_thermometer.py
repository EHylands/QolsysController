import logging

from .zwave_device import QolsysZWaveDevice

LOGGER = logging.getLogger(__name__)


class QolsysThermometer(QolsysZWaveDevice):
    def __init__(self, zwave_dict: dict[str, str]) -> None:
        super().__init__(zwave_dict)
        self._temprature_value = ""
        self._humidity_value = ""

    def update_raw(self, payload: bytes) -> None:
        LOGGER.debug("Raw Update (node%s) - payload: %s", self.node_id, payload.hex())

    def to_dict_thermometer(self) -> dict[str, str]:
        return {
            "temperature_value": self._temprature_value,
            "humidity_value": self._humidity_value,
        }
