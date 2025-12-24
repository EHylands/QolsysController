import logging

from .zwave_device import QolsysZWaveDevice

LOGGER = logging.getLogger(__name__)


class QolsysGarageDoor(QolsysZWaveDevice):
    def __init__(self) -> None:
        pass

    def update_raw(self, command: int, command_status: int, command_type: int, payload: list[int]) -> None:
        LOGGER.debug(
            "Raw Update (node%s) - command:%s status:%s type:%s payload:%s",
            self.node_id,
            command,
            command_status,
            command_type,
            payload,
        )
