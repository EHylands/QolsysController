import logging

from .zwave_device import QolsysZWaveDevice

LOGGER = logging.getLogger(__name__)


class QolsysEnergyClamp(QolsysZWaveDevice):
    def __init__(self, zwave_dict: dict[str, str]) -> None:
        super().__init__(zwave_dict)

    # Energy clamp only enables meter seter in base zwave_device class

    def update_raw(self, payload: bytes) -> None:
        pass
