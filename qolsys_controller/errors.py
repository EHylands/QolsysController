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

    def __init__(self,operation:dict) -> None:
        super().__init__("QolsysSqlError")

        line_table = f"QolsysSqlError - table:{operation.get('table',"")}"
        line_query = f"QolsysSqlError - query:{operation.get('query',"")}"
        line_columns = f"QolsysSqlError - columns:{operation.get('columns',"")}"
        line_content_values = f"QolsysSqlError - content_values:{operation.get('content_value',"")}"
        line_selection = f"QolsysSqlError - selection:{operation.get('selection',"")}"
        line_selection_argument = f"QolsysSqlError - selection_argument:{operation.get('selection_argument',"")}"

        error_string = f"\n{line_table}\n{line_query}\n{line_columns}\n{line_content_values}\n{line_selection}\n{line_selection_argument}"
        LOGGER.exception(error_string)




