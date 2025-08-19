import logging

from qolsys_controller.zwave_device import QolsysZWaveDevice

LOGGER = logging.getLogger(__name__)

class QolsysGeneric(QolsysZWaveDevice):

    def __init__(self,zwave_dict:dict) -> None:
        super().__init__(zwave_dict)
