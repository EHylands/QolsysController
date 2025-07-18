import logging
from collections.abc import Callable

LOGGER = logging.getLogger(__name__)

class QolsysObservable:
    def __init__(self):
        self._observers: list[Callable[[], None]] = []

    def register(self, observer: Callable[[], None]) -> None:
        #LOGGER.debug(f"Registering {repr(observer)} to {self} updates")
        self._observers.append(observer)

    def unregister(self, observer: Callable[[], None]) -> None:
        #LOGGER.debug(f"Unregistering {repr(observer)} from {self} updates")
        self._observers.remove(observer)

    def notify(self,**payload):
        #LOGGER.debug(f"Notifying {self} observers with: {payload}")
        for observer in self._observers:
            observer(self,**payload)