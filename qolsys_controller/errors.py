import logging

LOGGER = logging.getLogger(__name__)


class QolsysError(Exception):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)


class QolsysSslError(QolsysError):

    def __init__(self) -> None:
        super().__init__("QolsysSslError")


class QolsysMqttError(QolsysError):

    def __init__(self) -> None:
        super().__init__("QolsysMqttError")


class QolsysSqlError(QolsysError):

    def __init__(self, operation: dict) -> None:
        super().__init__("QolsysSqlError")

        table = f"QolsysSqlError - table:{operation.get('table', "")}"
        query = f"QolsysSqlError - query:{operation.get('query', "")}"
        columns = f"QolsysSqlError - columns:{operation.get('columns', "")}"
        content_values = f"QolsysSqlError - content_values:{operation.get('content_value', "")}"
        selection = f"QolsysSqlError - selection:{operation.get('selection', "")}"
        selection_argument = f"QolsysSqlError - selection_argument:{operation.get('selection_argument', "")}"

        e = f"""\n{table}\n{query}\n{columns}\n{content_values}\n{selection}\n{selection_argument}"""
        LOGGER.exception(e)
