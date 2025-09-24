import logging  # noqa: INP001
import sqlite3

from .table import QolsysTable

LOGGER = logging.getLogger(__name__)

class QolsysTableDimmerLight(QolsysTable):

    def __init__(self,db:sqlite3.Connection,cursor:sqlite3.Cursor) -> None:
        super().__init__(db,cursor)
        self._uri = "content://com.qolsys.qolsysprovider.DimmerLightsContentProvider/dimmerlight"
        self._table = "dimmerlight"
        self._abort_on_error = True

        self._columns = [
            "_id TEXT",
            "version",
            "opr",
            "partition_id",
            "dimmer_name",
            "status",
            "node_id",
            "level",
            "created_by",
            "created_date",
            "updated_by",
            "last_updated_date",
            "endpoint",
            "power_details",
            "paired_status",
        ]

        self._create_table()

    def insert(self, data:dict) -> None:
        self._cursor.execute(f"INSERT INTO {self.table} (_id,version,opr,partition_id,dimmer_name,status,node_id,level,created_by,created_date,updated_by,last_updated_date,endpoint,power_details,paired_status) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(
                            data.get("_id"),
                            data.get("version",""),
                            data.get("opr",""),
                            data.get("partition_id",""),
                            data.get("dimmer_name",""),
                            data.get("status",""),
                            data.get("node_id",""),
                            data.get("level",""),
                            data.get("created_by",""),
                            data.get("created_date",""),
                            data.get("updated_by",""),
                            data.get("last_updated_date",""),
                            data.get("endpoint",""),
                            data.get("power_details",""),
                            data.get("paired_status","")))

        self._db.commit()

