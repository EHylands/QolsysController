import logging  # noqa: INP001
import sqlite3

from .table import QolsysTable

LOGGER = logging.getLogger(__name__)

class QolsysTableZwaveOther(QolsysTable):

    def __init__(self,db:sqlite3.Connection,cursor:sqlite3.Cursor) -> None:
        super().__init__(db,cursor)
        self._uri = "content://com.qolsys.qolsysprovider.ZwaveOtherDeviceContentProvider/zwave_other"
        self._table = "zwave_other"
        self._abort_on_error = False

        self._columns = [
            "_id",
        ]

        self._create_table()

    def insert(self, data:dict) -> None:
        if data is not None:
            LOGGER.error("Please Report")
            LOGGER.error("Loading Table Format: %s",self.uri)
            LOGGER.error(data)

