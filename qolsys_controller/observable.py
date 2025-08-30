import logging
from collections.abc import Callable

LOGGER = logging.getLogger(__name__)

class QolsysObservable:
    def __init__(self) -> None:
        self._observers: list[Callable[[], None]] = []

        self._batch_update_active = False
        self._batch_update_change_detected = False

    def register(self, observer: Callable[[], None]) -> None:
        self._observers.append(observer)

    def unregister(self, observer: Callable[[], None]) -> None:
        self._observers.remove(observer)

    def notify(self,**payload) -> None:  # noqa: ANN003
        if self._batch_update_active:
            self._batch_update_change_detected = True
        else:
            for observer in self._observers:
                observer(self,**payload)

    def start_batch_update(self) -> None:
        self._batch_update_change_detected = False
        self._batch_update_active = True

    def end_batch_update(self) -> None:
        self._batch_update_active = False
        if self._batch_update_change_detected:
            self.notify()
