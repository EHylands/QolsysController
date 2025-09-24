import logging  # noqa: INP001
import sqlite3

from .table import QolsysTable

LOGGER = logging.getLogger(__name__)

class QolsysTableHistory(QolsysTable):

    def __init__(self,db:sqlite3.Connection,cursor:sqlite3.Cursor) -> None:
        super().__init__(db,cursor)
        self._uri = "content://com.qolsys.qolsysprovider.HistoryContentProvider/history"
        self._table = "history"
        self._abort_on_error = False

        self._columns = [
            "_id",
            "version",
            "opr",
            "partition_id",
            "device",
            "events",
            "time",
            "ack",
            "type",
            "feature1",
            "device_id",
        ]

        self._create_table()

    def insert(self, data:dict) -> None:
        self._cursor.execute(f"INSERT INTO {self.table} (_id,version,opr,partition_id,device,events,time,ack,type,feature1,device_id) VALUES (?,?,?,?,?,?,?,?,?,?,?)",(
            data.get("_id"),
            data.get("version",""),
            data.get("opr",""),
            data.get("partition_id",""),
            data.get("device",""),
            data.get("events",""),
            data.get("time",""),
            data.get("ack",""),
            data.get("type",""),
            data.get("feature1",""),
            data.get("device_id","")))

        self._db.commit()

