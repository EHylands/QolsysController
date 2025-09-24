import logging  # noqa: INP001
import sqlite3

from .table import QolsysTable

LOGGER = logging.getLogger(__name__)

class QolsysTableCountryLocale(QolsysTable):

    def __init__(self,db:sqlite3.Connection,cursor:sqlite3.Cursor) -> None:
        super().__init__(db,cursor)
        self._uri = "content://com.qolsys.qolsysprovider.CountryLocaleContentProvider/country_locale"
        self._table = "country_locale"
        self._abort_on_error = False

        self._columns = [
            "_id",
            "version",
            "opr",
            "partition_id",
            "country",
            "language",
            "alpha2_code",
            "language_code",
            "date_format_enum",
            "hour_format",
            "temp_format",
            "is_active",
            "date_separator",
            "zwave_region_frequency_code",
            "zwave_region_frequency",
            "zwave_region_prop_values",
        ]

        self._create_table()

    def insert(self, data:dict) -> None:
        self._cursor.execute(f"INSERT INTO {self.table} (_id,version,opr,partition_id,country,language,alpha2_code,language_code,date_format_enum,hour_format,temp_format,is_active,date_separator,zwave_region_frequency_code,zwave_region_frequency,zwave_region_prop_values) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(
            data.get("_id"),
            data.get("version",""),
            data.get("opr",""),
            data.get("partition_id",""),
            data.get("country",""),
            data.get("language",""),
            data.get("alpha2_code",""),
            data.get("language_code",""),
            data.get("date_format_enum",""),
            data.get("hour_format",""),
            data.get("temp_format",""),
            data.get("is_active",""),
            data.get("date_separator",""),
            data.get("zwave_region_frequency_code",""),
            data.get("zwave_region_frequency",""),
            data.get("zwave_region_prop_values","")))

        self._db.commit()

