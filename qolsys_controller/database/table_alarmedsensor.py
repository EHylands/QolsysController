import logging  # noqa: INP001
import sqlite3

from .table import QolsysTable

LOGGER = logging.getLogger(__name__)

class QolsysTableAlarmedSensor(QolsysTable):

    def __init__(self,db:sqlite3.Connection,cursor:sqlite3.Cursor) -> None:
        super().__init__(db,cursor)
        self._uri = "content://com.qolsys.qolsysprovider.AlarmedSensorProvider/alarmedsensor"
        self._table = "alarmedsensor"
        self._abort_on_error = True

        self._columns = [
            "_id",
            "partition_id",
            "silenced",
            "zone_id",
            "sgroup",
            "action",
            "timed_out",
            "type",
            "priority",
            "aseb_type",
        ]

        self._create_table()

    def insert(self, data:dict) -> None:
        self._cursor.execute(f"INSERT INTO {self.table} (_id,partition_id,silenced,zone_id,sgroup,action,timed_out,type,priority,aseb_type) VALUES (?,?,?,?,?,?,?,?,?,?)",(
            data.get("_id"),
            data.get("partition_id",""),
            data.get("silenced",""),
            data.get("zone_id",""),
            data.get("sgroup",""),
            data.get("action",""),
            data.get("timed_out",""),
            data.get("type",""),
            data.get("priority",""),
            data.get("aseb_type","")))

        self._db.commit()

