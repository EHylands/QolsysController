import logging
from typing import TYPE_CHECKING

from .zwave_device import QolsysZWaveDevice

if TYPE_CHECKING:
    from .controller import QolsysController

LOGGER = logging.getLogger(__name__)


class QolsysSmartSocket(QolsysZWaveDevice):
    def __init__(self, controller: "QolsysController", zwave_dict: dict[str, str]) -> None:
        super().__init__(controller, zwave_dict)

    def update_raw(self, payload: bytes) -> None:
        LOGGER.debug("Raw Update (node%s) - payload: %s", self.node_id, payload.hex())

    def to_dict_smart_socket(self) -> dict[str, str]:
        return {}
