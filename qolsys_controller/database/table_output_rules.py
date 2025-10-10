import logging  # noqa: INP001
import sqlite3

from .table import QolsysTable

LOGGER = logging.getLogger(__name__)


class QolsysTableOutputRules(QolsysTable):

    def __init__(self, db: sqlite3.Connection, cursor: sqlite3.Cursor) -> None:
        super().__init__(db, cursor)
        self._uri = "content://com.qolsys.qolsysprovider.OutputRulesContentProvider/output_rules"
        self._table = "output_rules"
        self._abort_on_error = False
        self._implemented = False

        self._columns = [
            "_id",
        ]

        self._create_table()
