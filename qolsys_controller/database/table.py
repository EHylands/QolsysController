import logging  # noqa: INP001
import sqlite3

from qolsys_controller.errors import QolsysSqlError

LOGGER = logging.getLogger(__name__)


class QolsysTable:

    def __init__(self, db: sqlite3.Connection, cursor: sqlite3.Cursor) -> None:
        self._db: sqlite3.Connection = db
        self._cursor: sqlite3.Cursor = cursor
        self._uri: str = ""
        self._table: str = ""
        self._columns: list[str] = []
        self._abort_on_error: bool = False
        self._implemented:bool = False

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

        try:
            query = f"CREATE TABLE {self._table} ({', '.join(column_defs)})"
            self._cursor.execute(query)
            self._db.commit()

        except sqlite3.Error as err:
            error = QolsysSqlError({
                "table": self.table,
                "query": query,
                "columns": self._columns,
            })

            if self._abort_on_error:
                raise error from err

    def clear(self) -> None:
        try:
            query = f"DELETE from {self.table}"
            self._cursor.execute(query)
            self._db.commit()

        except sqlite3.Error as err:
            error = QolsysSqlError({
                "table": self.table,
                "query": query,
                "columns": self._columns,
            })

            if self._abort_on_error:
                raise error from err

    def insert(self, data: dict) -> None:

        try:
            if not self._implemented and data is not None:
                LOGGER.warning("New Table format: %s", self.uri)
                LOGGER.warning("Table: %s", self.table)
                LOGGER.warning(data)
                LOGGER.warning("Please Report")
                return

            full_data = {col: data.get(col, "") for col in self._columns}

            new_columns = []
            for key in data:
                if key not in self._columns:
                    new_columns.append(key)

            # Warn if new column found in iq2meid database
            if new_columns:
                LOGGER.warning("New column found in iq2meid database")
                LOGGER.warning("Table: %s", self.table)
                LOGGER.warning("New Columns: %s", new_columns)
                LOGGER.warning("Please Report")

            col_str = ", ".join(full_data.keys())
            placeholder_str = ", ".join([f":{key}" for key in full_data])

            query = f"INSERT OR IGNORE INTO {self.table} ({col_str}) VALUES ({placeholder_str})"
            self._cursor.execute(query, full_data)
            self._db.commit()

        except sqlite3.Error as err:
            error = QolsysSqlError({
                "table": self.table,
                "query": query,
                "columns": self._columns,
            })

            if self._abort_on_error:
                raise error from err

    def update(self, selection: str | None, selection_argument: list | str | None, content_value: str | None) -> None:
        # selection: 'zone_id=?, parition_id=?'
        # Firmware 4.4.1: selection_argument: '[3,1]'
        # Firmware 4.6.1: selection_argument: ['3','1']
        # contentValues:{"partition_id":"0","sensorgroup":"safetymotion","sensorstatus":"Idle"}"

        # Firmware 4.4.1: seletion_argument is sent as a string and needs to be converted to an array
        if(type(selection_argument) is str):
            selection_argument = selection_argument.strip("[]")
            selection_argument = [item.strip() for item in selection_argument.split(",")]

        try:
            full_data = {}
            new_columns = []

            for key, value in content_value.items():
                if key in self._columns:
                    full_data[key] = value
                else:
                    new_columns.append(key)

            db_value = ",".join([f"{key}='{value}'" for key, value in full_data.items()])

            # Warn if new column found in iq2meid database
            if new_columns:
                LOGGER.warning("New column found in iq2meid database")
                LOGGER.warning("Table: %s", self.table)
                LOGGER.warning("New Columns: %s", new_columns)
                LOGGER.warning("Please Report")

            if selection:
                query = f"UPDATE {self.table} SET {db_value} WHERE {selection}"
                self._cursor.execute(query, selection_argument)
            else:
                query = f"UPDATE {self.table} SET {db_value}"
                self._cursor.execute(query)

            self._db.commit()

        except sqlite3.Error as err:
            error = QolsysSqlError({
                "table": self.table,
                "query": query,
                "columns": self._columns,
                "content_value": content_value,
                "selection": selection,
                "selection_argument": selection_argument,
            })

            if self._abort_on_error:
                raise error from err

    def delete(self, selection: str | None, selection_argument: list | str | None) -> None:
        # selection: 'zone_id=?, parition_id=?'
        # Firmware 4.4.1: selection_argument: '[3,1]'
        # Firmware 4.6.1: selection_argument: ['3','1']

        # Firmware 4.4.1: seletion_argument is sent as a string and needs to be converted to an array
        if(type(selection_argument) is str):
            selection_argument = selection_argument.strip("[]")
            selection_argument = [item.strip() for item in selection_argument.split(",")]

        try:
            if selection:
                query = f"DELETE FROM {self.table} WHERE {selection}"
                self._cursor.execute(query, selection_argument)
            else:
                self.clear()

            self._db.commit()

        except sqlite3.Error as err:
            error = QolsysSqlError({
                "table": self.table,
                "query": query,
                "columns": self._columns,
                "selection": selection,
                "selection_argument": selection_argument,
            })

            if self._abort_on_error:
                raise error from err
