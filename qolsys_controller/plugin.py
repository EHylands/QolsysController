import logging

from .observable import QolsysObservable
from .panel import QolsysPanel
from .settings import QolsysSettings
from .state import QolsysState

LOGGER = logging.getLogger(__name__)

class QolsysPlugin:
    def __init__(self,state:QolsysState,panel:QolsysPanel,settings:QolsysSettings) -> None:

        self._state = state
        self._panel = panel
        self._settings = settings

        self.connected = False
        self.connected_observer = QolsysObservable()

    def config(self) -> None:
        pass

    @property
    def state(self) -> QolsysState:
        return self._state

    @property
    def panel(self) -> QolsysPanel:
        return self._panel

    @property
    def settings(self) -> QolsysSettings:
        return self._settings
