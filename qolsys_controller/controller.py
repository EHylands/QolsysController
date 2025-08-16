import logging

from qolsys_controller.state import QolsysState
from qolsys_controller.panel import QolsysPanel
from qolsys_controller.pluginC4 import QolsysPluginC4
from qolsys_controller.pluginRemote import QolsysPluginRemote
from qolsys_controller.settings import QolsysSettings

LOGGER = logging.getLogger(__name__)

class QolsysController():

    def __init__(self,config_directory:str) -> None:

        # QolsysController Information
        self.plugin = None
        self._config_directory = config_directory
        self._state = QolsysState()
        self._panel = QolsysPanel(settings_directory=config_directory,state=self.state)
        self._settings = QolsysSettings()

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
                self.plugin = QolsysPluginRemote(self.state,self.panel,self.settings,self._config_directory)
                return
            
            case _:
                LOGGER.debug(f'Unknow Plugin Selected')
    


