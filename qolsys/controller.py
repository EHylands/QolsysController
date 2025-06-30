import logging

from qolsys.state import QolsysState
from qolsys.panel import QolsysPanel
from qolsys.plugin import QolsysPlugin
from qolsys.pluginC4 import QolsysPluginC4
from qolsys.pluginRemote import QolsysPluginRemote
from qolsys.settings import QolsysSettings

LOGGER = logging.getLogger(__name__)

class QolsysController():

    def __init__(self) -> None:

        # QolsysController Information
        self.plugin = None
        self._state = QolsysState()
        self._panel = QolsysPanel(settings_directory='./config/')
        self._settings = QolsysSettings(settings_directory='./config/',settings_file='pairing.status',)

    @property
    def state(self):
        return self._state
    
    @property
    def panel(self):
        return self._panel
    
    @property
    def settings(self):
        return self._settings

    def select_plugin(self,plugin: str):

        match plugin:

            case 'c4':
                LOGGER.debug(f'C4 Plugin Selected')
                self.plugin = QolsysPluginC4(self.state,self.panel,self.settings)
                return
            
            case 'remote':
                LOGGER.debug(f'Remote Plugin Selected')
                self.plugin = QolsysPluginRemote(self.state,self.panel,self.settings)
                return
            
            case _:
                LOGGER.debug(f'Unknow Plugin Selected')
    


