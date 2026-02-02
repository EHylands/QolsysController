from typing import Protocol, runtime_checkable


@runtime_checkable
class StatusProtocol(Protocol):
    def is_status_supported(self) -> bool: ...
    def malfunction(self) -> bool: ...
