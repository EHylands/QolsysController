import logging
from typing import TYPE_CHECKING

from qolsys_controller.protocol_zwave.device import QolsysZWaveDevice

if TYPE_CHECKING:
    from qolsys_controller.controller import QolsysController

LOGGER = logging.getLogger(__name__)


class QolsysGeneric(QolsysZWaveDevice):
    def __init__(self, controller: "QolsysController", zwave_dict: dict[str, str]) -> None:
        super().__init__(controller, zwave_dict)

    def update_raw(self, payload: bytes, endpoint: int = 0) -> None:
        super().update_raw(payload, endpoint)
