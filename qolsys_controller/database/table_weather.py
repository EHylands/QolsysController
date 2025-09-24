import logging  # noqa: INP001
import sqlite3

from .table import QolsysTable

LOGGER = logging.getLogger(__name__)

class QolsysTableWeather(QolsysTable):

    def __init__(self,db:sqlite3.Connection,cursor:sqlite3.Cursor) -> None:
        super().__init__(db,cursor)
        self._uri = "content://com.qolsys.qolsysprovider.ForecastWeatherContentProvider/weather"
        self._table = "weather"
        self._abort_on_error = False

        self._columns = [
            "_id",
            "version",
            "opr",
            "partition_id",
            "high_temp",
            "low_temp",
            "day_of_week",
            "condition",
            "icon",
            "precipitation",
            "current_weather_date",
        ]

        self._create_table()

    def insert(self, data:dict) -> None:
        self._cursor.execute(f"INSERT INTO {self.table} (_id,version,opr,partition_id,high_temp,low_temp,day_of_week,condition,icon,precipitation,current_weather_date) VALUES (?,?,?,?,?,?,?,?,?,?,?)",(
            data.get("_id"),
            data.get("version",""),
            data.get("opr",""),
            data.get("partition_id",""),
            data.get("high_temp",""),
            data.get("low_temp",""),
            data.get("day_of_week",""),
            data.get("condition",""),
            data.get("icon",""),
            data.get("precipitation",""),
            data.get("current_weather_date","")))

        self._db.commit()

