import logging

from qolsys_controller.state import QolsysState
from qolsys_controller.panel import QolsysPanel
from qolsys_controller.settings import QolsysSettings
from qolsys_controller.observable import QolsysObservable

LOGGER = logging.getLogger(__name__)

class QolsysPlugin():
    def __init__(self,state:QolsysState,panel:QolsysPanel,settings:QolsysSettings):
            
        self._state = state
        self._panel = panel
        self._settings = settings

        self.connected = False
        self.connected_observer = QolsysObservable()

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