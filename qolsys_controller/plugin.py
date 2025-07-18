import logging

from qolsys_controller.state import QolsysState
from qolsys_controller.panel import QolsysPanel
from qolsys_controller.settings import QolsysSettings

LOGGER = logging.getLogger(__name__)

class QolsysPlugin():
    def __init__(self,state:QolsysState,panel:QolsysPanel,settings:QolsysSettings):
            
        self._state = state
        self._panel = panel
        self._settings = settings

    def config(self):
        pass

    @property
    def state(self):
        return self._state
        
    @property
    def panel(self):
        return self._panel
        
    @property
    def settings(self):
        return self._settings