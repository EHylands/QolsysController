import logging  # noqa: INP001
import sqlite3

from .table import QolsysTable

LOGGER = logging.getLogger(__name__)

class QolsysTableZwaveAssociationGroup(QolsysTable):

    def __init__(self,db:sqlite3.Connection,cursor:sqlite3.Cursor) -> None:
        super().__init__(db,cursor)
        self._uri = "content://com.qolsys.qolsysprovider.ZwaveAssociationGroupContentProvider/zwave_association_group"
        self._table = "zwave_association_group"
        self._abort_on_error = False

        self._columns = [
            "_id",
            "version",
            "opr",
            "partition_id",
            "group_name",
            "associated_nodes",
            "group_id",
            "created_date",
            "last_updated_date",
            "group_command_class",
            "max_supported_nodes",
            "node_id",
            "endpoint",
        ]

        self._create_table()

    def insert(self, data:dict) -> None:
        self._cursor.execute(f"INSERT INTO {self.table} (_id,version,opr,partition_id,group_name,associated_nodes,group_id,created_date,last_updated_date,group_command_class,max_supported_nodes,node_id,endpoint) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",(
            data.get("_id"),
            data.get("version",""),
            data.get("opr",""),
            data.get("partition_id",""),
            data.get("group_name",""),
            data.get("associated_nodes",""),
            data.get("group_id",""),
            data.get("created_date",""),
            data.get("last_updated_date",""),
            data.get("group_command_class",""),
            data.get("max_supported_nodes",""),
            data.get("node_id",""),
            data.get("endpoint","")))

        self._db.commit()

