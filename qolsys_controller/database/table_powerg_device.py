import logging  # noqa: INP001
import sqlite3

from .table import QolsysTable

LOGGER = logging.getLogger(__name__)

class QolsysTablePowerGDevice(QolsysTable):

    def __init__(self,db:sqlite3.Connection,cursor:sqlite3.Cursor) -> None:
        super().__init__(db,cursor)
        self._uri = "content://com.qolsys.qolsysprovider.PowerGDeviceContentProvider/powerg_device"
        self._table = "powerg_device"
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

