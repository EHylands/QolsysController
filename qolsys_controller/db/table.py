import logging  # noqa: INP001
import sqlite3

LOGGER = logging.getLogger(__name__)

class QolsysTable:

    def __init__(self,db:sqlite3.Connection,cursor:sqlite3.Cursor) -> None:
        self._db:sqlite3.Connection = db
        self._cursor:sqlite3.Cursor = cursor
        self._uri:str = ""
        self._table:str = ""
        self._columns:list[str] = []

    @property
    def uri(self) -> str:
        return self._uri
    @property
    def table(self) -> str:
        return self._table

    def _create_table(self) -> None:
        if not self._columns:
            msg = "The column list must not be empty."
            raise ValueError(msg)

        primary_key = self._columns[0]
        other_columns = self._columns[1:]

        column_defs = [f"{primary_key} TEXT PRIMARY KEY"]
        column_defs += [f"{col} TEXT" for col in other_columns]

        self._cursor.execute(f"CREATE TABLE {self._table} ({', '.join(column_defs)})")
        self._db.commit()

    def clear(self) -> None:
        self._cursor.execute(f"DELETE from {self.table}")
        self._db.commit()

    def update(self,selection:str,selection_argument:str,content_value:str) -> None:
        # selection: 'zone_id=?, parition_id=?'  # noqa: ERA001
        # selection_argument: '[3,1]'  # noqa: ERA001
        #  "contentValues":{"partition_id":"0","sensorgroup":"safetymotion","sensorstatus":"Idle"}"

        # Panel is sending query parameter for db update in text string
        # Have not found a way to make it work with parametrized query yet
        # Using f string concat for moment ...

        # New Values to update in table
        db_value = ",".join([f"{key}='{value}'" for key,value in content_value.items()])

        # Selection Argument
        selection_argument = selection_argument.strip("[]")
        selection_argument = [item.strip() for item in selection_argument.split(",")]

        for i in selection_argument:
            selection = selection.replace("?",f"'{i}'",1)

         # Final query
        self._cursor.execute(f"UPDATE {self.table} SET {db_value} WHERE {selection}")
        self._db.commit()

    def insert(self) -> None:
        pass

    def delete(self,selection:str,selection_argument:str) -> None:
        # selection: 'zone_id=?, parition_id=?'  # noqa: ERA001
        # selection_argument: '[3,1]'  # noqa: ERA001

        selection_argument = selection_argument.strip("[]")
        selection_argument = [item.strip() for item in selection_argument.split(",")]

        # Replace '?' in selection string with selection_argument
        for i in selection_argument:
            selection = selection.replace("?",f"'{i}'",1)

        self._cursor.execute(f"DELETE FROM {self.table} WHERE {selection}")
        self._db.commit()
