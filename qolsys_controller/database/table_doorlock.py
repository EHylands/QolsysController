import logging  # noqa: INP001
import sqlite3

from .table import QolsysTable

LOGGER = logging.getLogger(__name__)

class QolsysTableDoorLock(QolsysTable):

    def __init__(self,db:sqlite3.Connection,cursor:sqlite3.Cursor) -> None:
        super().__init__(db,cursor)
        self._uri = "content://com.qolsys.qolsysprovider.DoorLocksContentProvider/doorlock"
        self._table = "doorlock"
        self._abort_on_error = True

        self._columns = [
            "_id",
            "version",
            "opr",
            "partition_id",
            "doorlock_name",
            "status",
            "node_id",
            "created_by",
            "created_date",
            "updated_by",
            "last_updated_date",
            "remote_arming",
            "keyfob_arming",
            "panel_arming",
            "endpoint",
            "paired_status",
        ]

        self._create_table()

    def insert(self, data:dict) -> None:
        self._cursor.execute(f"INSERT INTO {self.table} (_id,version,opr,partition_id,doorlock_name,status,node_id,remote_arming,keyfob_arming,panel_arming,created_by,created_date,updated_by,last_updated_date,endpoint,paired_status) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(
            data.get("_id"),
            data.get("version",""),
            data.get("opr",""),
            data.get("partition_id",""),
            data.get("doorlock_name",""),
            data.get("status",""),
            data.get("node_id",""),
            data.get("remote_arming",""),
            data.get("keyfob_arming",""),
            data.get("panel_arming",""),
            data.get("created_by",""),
            data.get("created_date",""),
            data.get("updated_by",""),
            data.get("last_updated_date",""),
            data.get("endpoint",""),
            data.get("paired_status","")))

        self._db.commit()

