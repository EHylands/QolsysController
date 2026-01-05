from collections.abc import Callable
from typing import Any


class QolsysObservable_v2:
    def __init__(self) -> None:
        self._observers: dict[str, Any] = {}

    def subscribe(self, event_name: str, callback: Callable[[], None]) -> None:
        self._observers.setdefault(event_name, []).append(callback)

    def publish(self, event_name: str, *args: Any, **kwargs: Any) -> None:
        for callback in self._observers.get(event_name, []):
            callback(*args, **kwargs)
