import logging
from typing import TYPE_CHECKING

from .zwave_device import QolsysZWaveDevice

if TYPE_CHECKING:
    from .controller import QolsysController

LOGGER = logging.getLogger(__name__)


class QolsysThermometer(QolsysZWaveDevice):
    def __init__(self, controller: "QolsysController", zwave_dict: dict[str, str]) -> None:
        super().__init__(controller, zwave_dict)
        self._temprature_value = ""
        self._humidity_value = ""

    def update_raw(self, payload: bytes, endpoint: int = 0) -> None:
        super().update_raw(payload, endpoint)

    def to_dict_thermometer(self) -> dict[str, str]:
        return {
            "temperature_value": self._temprature_value,
            "humidity_value": self._humidity_value,
        }
