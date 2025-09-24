import logging  # noqa: INP001
import sqlite3

from .table import QolsysTable

LOGGER = logging.getLogger(__name__)

class QolsysTableAutomation(QolsysTable):

    def __init__(self,db:sqlite3.Connection,cursor:sqlite3.Cursor) -> None:
        super().__init__(db,cursor)
        self._uri = "content://com.qolsys.qolsysprovider.AutomationDeviceContentProvider/automation"
        self._table = "automation"
        self._abort_on_error = False

        self._columns = [
            "_id",
            "virtual_node_id",
            "version",
            "opr",
            "partition_id",
            "end_point",
            "extras",
            "is_autolocking_enabled",
            "device_type",
            "endpoint_secure_cmd_classes",
            "automation_id",
            "device_name",
            "protocol",
            "node_battery_level_value",
            "state",
            "last_updated_date",
            "manufacturer_id",
            "endpoint_cmd_classes",
            "device_id",
            "nodeid_cmd_classes",
            "is_device_hidden",
            "nodeid_secure_cmd_classes",
            "created_date",
            "status",
        ]

        self._create_table()

    def insert(self, data:dict) -> None:
        self._cursor.execute(f"INSERT INTO {self.table} (_id,virtual_node_id,version,opr,partition_id,end_point,extras,is_autolocking_enabled,device_type,endpoint_secure_cmd_classes,automation_id,device_name,protocol,node_battery_level_value,state,last_updated_date,manufacturer_id,endpoint_cmd_classes,device_id,nodeid_cmd_classes,is_device_hidden,nodeid_secure_cmd_classes,created_date,status) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(
            data.get("_id"),
            data.get("virtual_node_id",""),
            data.get("version",""),
            data.get("opr",""),
            data.get("partition_id",""),
            data.get("end_point",""),
            data.get("extras",""),
            data.get("is_autolocking_enabled",""),
            data.get("device_type",""),
            data.get("endpoint_secure_cmd_classes",""),
            data.get("automation_id",""),
            data.get("device_name",""),
            data.get("protocol",""),
            data.get("node_battery_level_value",""),
            data.get("state",""),
            data.get("last_updated_date",""),
            data.get("manufacturer_id",""),
            data.get("endpoint_cmd_classes",""),
            data.get("device_id",""),
            data.get("nodeid_cmd_classes",""),
            data.get("is_device_hidden",""),
            data.get("nodeid_secure_cmd_classes",""),
            data.get("created_date",""),
            data.get("status","")))

        self._db.commit()

