import logging  # noqa: INP001
import sqlite3

from .table import QolsysTable

LOGGER = logging.getLogger(__name__)

class QolsysTableZwaveHistory(QolsysTable):

    def __init__(self,db:sqlite3.Connection,cursor:sqlite3.Cursor) -> None:
        super().__init__(db,cursor)
        self._uri = "content://com.qolsys.qolsysprovider.ZDeviceHistoryContentProvider/zwave_history"
        self._table = "zwave_history"
        self._abort_on_error = False

        self._columns = [
            "_id",
            "version",
            "opr",
            "partition_id",
            "node_id",
            "device_name",
            "source",
            "event",
            "request",
            "response",
            "created_date",
            "updated_date",
            "last_updated_by",
            "field_type",
            "ack",
            "protocol",
        ]

        self._create_table()

    def insert(self, data:dict) -> None:
        self._cursor.execute(f"INSERT INTO {self.table} (_id,version,opr,partition_id,node_id,device_name,source,event,request,response,created_date,updated_date,last_updated_by,field_type,ack,protocol) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(
            data.get("_id"),
            data.get("version",""),
            data.get("opr",""),
            data.get("partition_id",""),
            data.get("node_id",""),
            data.get("device_name",""),
            data.get("source",""),
            data.get("event",""),
            data.get("request",""),
            data.get("response",""),
            data.get("created_date",""),
            data.get("updated_date",""),
            data.get("last_updated_by",""),
            data.get("field_type",""),
            data.get("ack",""),
            data.get("protocol","")))

        self._db.commit()

