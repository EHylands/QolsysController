import logging  # noqa: INP001
import sqlite3

from .table import QolsysTable

LOGGER = logging.getLogger(__name__)

class QolsysTableTcc(QolsysTable):

    def __init__(self,db:sqlite3.Connection,cursor:sqlite3.Cursor) -> None:
        super().__init__(db,cursor)
        self._uri = "content://com.qolsys.qolsysprovider.TccContentProvider/tcc"
        self._table = "tcc"
        self._abort_on_error = False

        self._columns = [
            "tableName",
            "counter",
        ]

        self._create_table()

    def insert(self, data:dict) -> None:
        # panel sends content://com.qolsys.qolsysprovider.PowerGDeviceContentProvider/powerg_device' twice
        self._cursor.execute(f"INSERT OR IGNORE INTO {self.table} (tableName,counter) VALUES (?,?)",(
            data.get("tableName"),
            data.get("counter","")))

        self._db.commit()
