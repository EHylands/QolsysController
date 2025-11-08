#!/usr/bin/env python3
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from qolsys_controller.plugin import QolsysPlugin

from .panel import QolsysPanel
from .plugin_c4 import QolsysPluginC4
from .plugin_remote import QolsysPluginRemote
from .settings import QolsysSettings
from .state import QolsysState

LOGGER = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .plugin import QolsysPlugin

class QolsysController:

    def __init__(self) -> None:

        # QolsysController Information
        self._plugin: QolsysPlugin | None = None
        self._state = QolsysState(self)
        self._settings = QolsysSettings(self)
        self._panel = QolsysPanel(self)

    @property
    def state(self) -> QolsysState:
        return self._state

    @property
    def plugin(self) -> QolsysPlugin:
        return self._plugin

    @property
    def panel(self) -> QolsysPanel:
        return self._panel

    @property
    def settings(self) -> QolsysSettings:
        return self._settings

    def select_plugin(self, plugin: str) -> None:

        match plugin:

            case "c4":
                LOGGER.debug("C4 Plugin Selected")
                self._plugin = QolsysPluginC4(self)
                return

            case "remote":
                LOGGER.debug("Remote Plugin Selected")
                self._plugin = QolsysPluginRemote(self)
                return

            case _:
                LOGGER.error("Unknow Plugin Selected")
