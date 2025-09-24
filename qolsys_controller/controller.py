#!/usr/bin/env python3
import logging

from .panel import QolsysPanel
from .plugin_c4 import QolsysPluginC4
from .plugin_remote import QolsysPluginRemote
from .settings import QolsysSettings
from .state import QolsysState

LOGGER = logging.getLogger(__name__)

class QolsysController:

    def __init__(self,config_directory:str) -> None:

        # QolsysController Information
        self.plugin = None
        self._config_directory = config_directory
        self._state = QolsysState()
        self._panel = QolsysPanel(settings_directory=config_directory,state=self.state)
        self._settings = QolsysSettings()

    @property
    def state(self) -> QolsysState:
        return self._state

    @property
    def panel(self) -> QolsysPanel:
        return self._panel

    @property
    def settings(self) -> QolsysSettings:
        return self._settings

    def select_plugin(self,plugin: str) -> None:

        match plugin:

            case "c4":
                LOGGER.debug("C4 Plugin Selected")
                self.plugin = QolsysPluginC4(self.state,self.panel,self.settings)
                return

            case "remote":
                LOGGER.debug("Remote Plugin Selected")
                self.plugin = QolsysPluginRemote(self.state,self.panel,self.settings,self._config_directory)
                return

            case _:
                LOGGER.debug("Unknow Plugin Selected")


