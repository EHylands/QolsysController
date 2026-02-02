import logging
from typing import TYPE_CHECKING

from .device import QolsysZWaveDevice

if TYPE_CHECKING:
    from qolsys_controller.controller import QolsysController

LOGGER = logging.getLogger(__name__)


class QolsysEnergyClamp(QolsysZWaveDevice):
    def __init__(self, controller: "QolsysController", zwave_dict: dict[str, str]) -> None:
        super().__init__(controller, zwave_dict)

    # Energy clamp only enables meter seter in base zwave_device class

    def update_raw(self, payload: bytes, endpoint: int = 0) -> None:
        super().update_raw(payload, endpoint)
