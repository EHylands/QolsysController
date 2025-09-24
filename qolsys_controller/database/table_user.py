import logging  # noqa: INP001
import sqlite3

from .table import QolsysTable

LOGGER = logging.getLogger(__name__)

class QolsysTableUser(QolsysTable):

    def __init__(self,db:sqlite3.Connection,cursor:sqlite3.Cursor) -> None:
        super().__init__(db,cursor)
        self._uri = "content://com.qolsys.qolsysprovider.UserContentProvider/user"
        self._table = "user"
        self._abort_on_error = False

        self._columns = [
            "_id",
            "version",
            "opr",
            "partition_id",
            "username",
            "userPin",
            "expirydate",
            "usertype",
            "userid",
            "lastname",
            "check_in",
            "hash_user",
        ]

        self._create_table()

    def insert(self, data:dict) -> None:
        self._cursor.execute(f"INSERT INTO {self.table} (_id,version,opr,partition_id,username,userPin,expirydate,usertype,userid,lastname,check_in,hash_user) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",(
            data.get("_id"),
            data.get("version",""),
            data.get("opr",""),
            data.get("partition_id",""),
            data.get("username",""),
            data.get("userPin",""),
            data.get("expirydate",""),
            data.get("usertype",""),
            data.get("userid",""),
            data.get("lastname",""),
            data.get("check_in",""),
            data.get("hash_user","")))

        self._db.commit()

