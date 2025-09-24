import logging  # noqa: INP001
import sqlite3

from .table import QolsysTable

LOGGER = logging.getLogger(__name__)

class QolsysTableTroubleConditions(QolsysTable):

    def __init__(self,db:sqlite3.Connection,cursor:sqlite3.Cursor) -> None:
        super().__init__(db,cursor)
        self._uri = "content://com.qolsys.qolsysprovider.TroubleConditionsContentProvider/trouble_conditions"
        self._table = "trouble_conditions"
        self._abort_on_error = False

        self._columns = [
            "_id",
            "version",
            "opr",
            "partition_id",
            "device_id",
            "device_name",
            "trouble_condition",
            "status",
            "time",
        ]

        self._create_table()

    def insert(self, data:dict) -> None:
        self._cursor.execute(f"INSERT INTO {self.table} (_id,version,opr,partition_id,device_id,device_name,trouble_condition,status,time) VALUES (?,?,?,?,?,?,?,?,?)",(
            data.get("_id"),
            data.get("version",""),
            data.get("opr",""),
            data.get("partition_id",""),
            data.get("device_id",""),
            data.get("device_name",""),
            data.get("trouble_condition",""),
            data.get("status",""),
            data.get("time","")))

        self._db.commit()

