import logging  # noqa: INP001
import sqlite3

from .table import QolsysTable

LOGGER = logging.getLogger(__name__)

class QolsysTableHeatMap(QolsysTable):

    def __init__(self,db:sqlite3.Connection,cursor:sqlite3.Cursor) -> None:
        super().__init__(db,cursor)
        self._uri = "content://com.qolsys.qolsysprovider.HeatMapContentProvider/heat_map"
        self._table = "heat_map"
        self._abort_on_error = False

        self._columns = [
            "_id",
            "version",
            "opr",
            "partition_id",
            "userid",
            "fragment_id",
            "element_id",
            "count",
            "time_stamp",
        ]

        self._create_table()

    def insert(self, data:dict) -> None:
        self._cursor.execute(f"INSERT INTO {self.table} (_id,version,opr,partition_id,userid,fragment_id,element_id,count,time_stamp) VALUES (?,?,?,?,?,?,?,?,?)",(
            data.get("_id"),
            data.get("version",""),
            data.get("opr",""),
            data.get("partition_id",""),
            data.get("userid",""),
            data.get("fragment_id",""),
            data.get("element_id",""),
            data.get("count",""),
            data.get("time_stamp","")))

        self._db.commit()

