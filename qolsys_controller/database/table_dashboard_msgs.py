import logging  # noqa: INP001
import sqlite3

from .table import QolsysTable

LOGGER = logging.getLogger(__name__)

class QolsysTableDashboardMsgs(QolsysTable):

    def __init__(self,db:sqlite3.Connection,cursor:sqlite3.Cursor) -> None:
        super().__init__(db,cursor)
        self._uri = "content://com.qolsys.qolsysprovider.DashboardMessagesContentProvider/dashboard_msgs"
        self._table = "dashboard_msgs"
        self._abort_on_error = False

        self._columns = [
            "_id",
            "version",
            "opr",
            "partition_id",
            "msg_id",
            "title",
            "description",
            "received_time",
            "start_time",
            "end_time",
            "read",
            "mime_type",
        ]

        self._create_table()

    def insert(self, data:dict) -> None:
        self._cursor.execute(f"INSERT INTO {self.table} (_id,version,opr,partition_id,msg_id,title,description,received_time,start_time,end_time,read,mime_type) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",(
            data.get("_id"),
            data.get("version"),
            data.get("opr"),
            data.get("partition_id"),
            data.get("msg_id"),
            data.get("title"),
            data.get("description"),
            data.get("received_time"),
            data.get("start_time"),
            data.get("end_time"),
            data.get("read"),
            data.get("mime_type")))

        self._db.commit()

