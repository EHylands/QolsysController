import logging
from typing import Any

LOGGER = logging.getLogger(__name__)


class QolsysError(Exception):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class QolsysUserCodeError(QolsysError):
    def __init__(self) -> None:
        super().__init__("QolsysUserCodeError")


class QolsysSslError(QolsysError):
    def __init__(self) -> None:
        super().__init__("QolsysSslError")


class QolsysMqttError(QolsysError):
    def __init__(self) -> None:
        super().__init__("QolsysMqttError")


class QolsysConfigError(QolsysError):
    def __init__(self, message: str) -> None:
        super().__init__(f"QolsysConfigError - {message}")


class QolsysSqlError(QolsysError):
    def __init__(self, operation: dict[str, Any]) -> None:
        super().__init__("QolsysSqlError")

        table = f"QolsysSqlError - table:{operation.get('table', '')}"
        query = f"QolsysSqlError - query:{operation.get('query', '')}"
        columns = f"QolsysSqlError - columns:{operation.get('columns', '')}"
        content_values = f"QolsysSqlError - content_values:{operation.get('content_value', '')}"
        selection = f"QolsysSqlError - selection:{operation.get('selection', '')}"
        selection_argument = f"QolsysSqlError - selection_argument:{operation.get('selection_argument', '')}"

        e = f"""\n{table}\n{query}\n{columns}\n{content_values}\n{selection}\n{selection_argument}"""
        LOGGER.exception(e)


class QolsysOperationError(Exception):
    """Base exception for Qolsys operation failures."""

    pass


class InvalidVirtualNodeError(QolsysOperationError):
    def __init__(self, node_id: str | int):
        super().__init__(f"Invalid vitual_node_id: {node_id}")
        self.node_id = node_id


class InvalidEndpointError(QolsysOperationError):
    def __init__(self, node_id: str | int, endpoint: str | int):
        super().__init__(f"Invalid endpoint {endpoint} for node {node_id}")
        self.node_id = node_id
        self.endpoint = endpoint


class ServiceNotFoundError(QolsysOperationError):
    def __init__(self, node_id: str, endpoint: str, service_type: str):
        super().__init__(f"No :{service_type} for node {node_id} endpoint {endpoint}")
        self.node_id = node_id
        self.endpoint = endpoint
        self.service_type = service_type


class CommandExecutionError(QolsysOperationError):
    def __init__(self, message: str):
        super().__init__(message)
