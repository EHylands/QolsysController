from __future__ import annotations

import logging
from abc import abstractmethod
from typing import TYPE_CHECKING

from .observable import QolsysObservable

LOGGER = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .controller import QolsysController


class QolsysPlugin:
    def __init__(self, controller: QolsysController) -> None:
        self._controller = controller
        self.connected = False
        self.connected_observer = QolsysObservable()

    @abstractmethod
    def config(self) -> None:
        pass

