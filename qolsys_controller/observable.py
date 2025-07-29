import logging
from collections.abc import Callable

LOGGER = logging.getLogger(__name__)

class QolsysObservable:
    def __init__(self):
        self._observers: list[Callable[[], None]] = []

        self._batch_update_active = False
        self._batch_update_change_detected = False

    def register(self, observer: Callable[[], None]) -> None:
        #LOGGER.debug(f"Registering {repr(observer)} to {self} updates")
        self._observers.append(observer)

    def unregister(self, observer: Callable[[], None]) -> None:
        #LOGGER.debug(f"Unregistering {repr(observer)} from {self} updates")
        self._observers.remove(observer)

    def notify(self,**payload):
        LOGGER.debug(f"Notifying {self} observers with: {payload}")
        if self._batch_update_active:
            self._batch_update_change_detected = True
        else:
            LOGGER.debug('notify')
            for observer in self._observers:
                observer(self,**payload)

    def start_batch_update(self):
        self._batch_update_change_detected = False
        self._batch_update_active = True

    def end_batch_update(self):
        self._batch_update_active = False
        if self._batch_update_change_detected:
            self.notify()

        
