import logging  # noqa: INP001
import sqlite3

from .table import QolsysTable

LOGGER = logging.getLogger(__name__)

class QolsysTableThermostat(QolsysTable):

    def __init__(self,db:sqlite3.Connection,cursor:sqlite3.Cursor) -> None:
        super().__init__(db,cursor)
        self._uri = "content://com.qolsys.qolsysprovider.ThermostatsContentProvider/thermostat"
        self._table = "thermostat"
        self._abort_on_error = False

        self._columns = [
            "_id",
            "version",
            "opr",
            "partition_id",
            "thermostat_id",
            "thermostat_name",
            "current_temp",
            "target_cool_temp",
            "target_heat_temp",
            "target_temp",
            "power_usage",
            "thermostat_mode",
            "thermostat_mode_bitmask",
            "fan_mode",
            "fan_mode_bitmask",
            "set_point_mode",
            "set_point_mode_bitmask",
            "node_id",
            "created_by",
            "created_date",
            "updated_by",
            "last_updated_date",
            "thermostat_mode_updated_time",
            "fan_mode_updated_time",
            "set_point_mode_updated_time",
            "target_cool_temp_updated_time",
            "target_heat_temp_updated_time",
            "current_temp_updated_time",
            "device_temp_unit",
            "endpoint",
            "paired_status",
            "configuration_parameter",
        ]

        self._create_table()

    def insert(self, data:dict) -> None:
        self._cursor.execute(f"INSERT INTO {self.table} (_id,version,opr,partition_id,thermostat_id,thermostat_name,current_temp,target_cool_temp,target_heat_temp,target_temp,power_usage,thermostat_mode,thermostat_mode_bitmask,fan_mode,fan_mode_bitmask,set_point_mode,set_point_mode_bitmask,node_id,created_by,created_date,updated_by,last_updated_date,thermostat_mode_updated_time,fan_mode_updated_time,set_point_mode_updated_time,target_cool_temp_updated_time,target_heat_temp_updated_time,current_temp_updated_time,device_temp_unit,endpoint,paired_status,configuration_parameter) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(
            data.get("_id"),
            data.get("version",""),
            data.get("opr",""),
            data.get("partition_id",""),
            data.get("thermostat_id",""),
            data.get("thermostat_name",""),
            data.get("current_temp",""),
            data.get("target_cool_temp",""),
            data.get("target_heat_temp",""),
            data.get("target_temp",""),
            data.get("power_usage",""),
            data.get("thermostat_mode",""),
            data.get("thermostat_mode_bitmask,fan_mode",""),
            data.get("fan_mode_bitmask,set_point_mode",""),
            data.get("set_point_mode_bitmask",""),
            data.get("node_id",""),
            data.get("created_by",""),
            data.get("created_date",""),
            data.get("updated_by",""),
            data.get("last_updated_date",""),
            data.get("thermostat_mode_updated_time",""),
            data.get("fan_mode_updated_time",""),
            data.get("set_point_mode_updated_time",""),
            data.get("target_cool_temp_updated_time",""),
            data.get("target_heat_temp_updated_time",""),
            data.get("current_temp_updated_time",""),
            data.get("device_temp_unit",""),
            data.get("endpoint",""),
            data.get("paired_status",""),
            data.get("configuration_parameter","")))

        self._db.commit()

