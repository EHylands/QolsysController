import logging

from .zwave_device import QolsysZWaveDevice

LOGGER = logging.getLogger(__name__)


class QolsysGeneric(QolsysZWaveDevice):
    def __init__(self, zwave_dict: dict[str, str]) -> None:
        super().__init__(zwave_dict)
