import logging

from .zwave_device import QolsysZWaveDevice

LOGGER = logging.getLogger(__name__)

class QolsysOutlet(QolsysZWaveDevice):

    def __init__(self) -> None:
        pass
