import logging  # noqa: INP001
import sqlite3

from .table import QolsysTable

LOGGER = logging.getLogger(__name__)

class QolsysTableState(QolsysTable):

    def __init__(self,db:sqlite3.Connection,cursor:sqlite3.Cursor) -> None:
        super().__init__(db,cursor)
        self._uri = "content://com.qolsys.qolsysprovider.StateContentProvider/state"
        self._table = "state"
        self._abort_on_error = True

        self._columns = [
            "_id",
            "version",
            "opr",
            "partition_id",
            "name",
            "value",
            "extraparams",
        ]

        self._create_table()

    def insert(self, data:dict) -> None:
        self._cursor.execute(f"INSERT INTO {self.table} (_id,version,opr,partition_id,name,value,extraparams) VALUES (?,?,?,?,?,?,?)",(
            data.get("_id"),
            data.get("version",""),
            data.get("opr",""),
            data.get("partition_id",""),
            data.get("name",""),
            data.get("value"),
            data.get("extraparams","")))

        self._db.commit()

