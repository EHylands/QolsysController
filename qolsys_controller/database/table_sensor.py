import logging  # noqa: INP001
import sqlite3

from .table import QolsysTable

LOGGER = logging.getLogger(__name__)

class QolsysTableSensor(QolsysTable):

    def __init__(self,db:sqlite3.Connection,cursor:sqlite3.Cursor) -> None:
        super().__init__(db,cursor)
        self._uri = "content://com.qolsys.qolsysprovider.SensorContentProvider/sensor"
        self._table = "sensor"
        self._abort_on_error = True

        self._columns = [
            "_id",
            "version",
            "opr",
            "partition_id",
            "ac_status",
            "sensorid",
            "sensortype",
            "sensorname",
            "sensorgroup",
            "chimetype",
            "sensorstatus",
            "time",
            "sensorstate",
            "sensortts",
            "zoneid",
            "frame_id",
            "zone_alarm_type",
            "zone_equipment_code",
            "zone_physical_type",
            "zone_type",
            "zone_rf_sensor",
            "zone_supervised",
            "zone_two_way_voice_enabled",
            "zone_reporting_enabled",
            "battery_status",
            "created_date",
            "created_by",
            "updated_date",
            "updated_by",
            "frame_count",
            "frame_type",
            "current_capability",
            "shortID",
            "diag_24hr",
            "allowdisarming",
            "device_capability",
            "sub_type",
            "signal_source",
            "powerg_manufacture_id",
            "parent_node",
            "latestdBm",
            "averagedBm",
            "serial_number",
            "extras",
        ]

        self._create_table()

    def insert(self, data:dict) -> None:
        self._cursor.execute(f"INSERT INTO {self.table} (_id,version,opr,partition_id,sensorid,sensortype,sensorname,sensorgroup,chimetype,sensorstatus,time,sensorstate,sensortts,zoneid,frame_id,zone_alarm_type,zone_equipment_code,zone_physical_type,zone_type,zone_rf_sensor,zone_supervised,zone_two_way_voice_enabled, zone_reporting_enabled, battery_status,created_date,created_by,updated_date,updated_by,frame_count,frame_type,current_capability,shortID,diag_24hr,allowdisarming,device_capability,sub_type, signal_source, powerg_manufacture_id,parent_node,latestdBm,averagedBm,serial_number,extras,ac_status) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(
            data.get("_id"),
            data.get("version",""),
            data.get("opr",""),
            data.get("partition_id",""),
            data.get("sensorid",""),
            data.get("sensortype",""),
            data.get("sensorname",""),
            data.get("sensorgroup",""),
            data.get("chimetype",""),
            data.get("sensorstatus",""),
            data.get("time",""),
            data.get("sensorstate",""),
            data.get("sensortts",""),
            data.get("zoneid",""),
            data.get("frame_id",""),
            data.get("zone_alarm_type",""),
            data.get("zone_equipment_code",""),
            data.get("zone_physical_type",""),
            data.get("zone_type",""),
            data.get("zone_rf_sensor",""),
            data.get("zone_supervised",""),
            data.get("zone_two_way_voice_enabled",""),
            data.get("zone_reporting_enabled",""),
            data.get("battery_status",""),
            data.get("created_date",""),
            data.get("created_by",""),
            data.get("updated_date",""),
            data.get("updated_by",""),
            data.get("frame_count",""),
            data.get("frame_type",""),
            data.get("current_capability",""),
            data.get("shortID",""),
            data.get("diag_24hr",""),
            data.get("allowdisarming",""),
            data.get("device_capability",""),
            data.get("sub_type",""),
            data.get("signal_source",""),
            data.get("powerg_manufacture_id",""),
            data.get("parent_node",""),
            data.get("latestdBm",""),
            data.get("averagedBm",""),
            data.get("serial_number",""),
            data.get("extras",""),
            data.get("ac_status","")))

        self._db.commit()
