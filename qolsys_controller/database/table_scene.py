import logging  # noqa: INP001
import sqlite3

from .table import QolsysTable

LOGGER = logging.getLogger(__name__)

class QolsysTableScene(QolsysTable):

    def __init__(self,db:sqlite3.Connection,cursor:sqlite3.Cursor) -> None:
        super().__init__(db,cursor)
        self._uri = "content://com.qolsys.qolsysprovider.SceneContentProvider/scene"
        self._table = "scene"
        self._abort_on_error = False

        self._columns = [
            "_id",
            "version",
            "opr",
            "partition_id",
            "scene_id",
            "name",
            "icon",
            "color",
            "flags",
            "ack",
            "create_time",
            "created_by",
            "update_time",
            "updated_by",
        ]

        self._create_table()

    def insert(self, data:dict) -> None:
        self._cursor.execute(f"INSERT INTO {self.table} (_id,version,opr,partition_id,scene_id,name,icon,color,flags,ack,create_time,created_by,update_time,updated_by) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(
            data.get("_id"),
            data.get("version",""),
            data.get("opr",""),
            data.get("partition_id",""),
            data.get("scene_id",""),
            data.get("name",""),
            data.get("icon",""),
            data.get("color",""),
            data.get("flags",""),
            data.get("ack",""),
            data.get("create_time",""),
            data.get("created_by",""),
            data.get("update_time",""),
            data.get("updated_by","")))

        self._db.commit()
