import logging  # noqa: INP001
import sqlite3

from .table import QolsysTable

LOGGER = logging.getLogger(__name__)

class QolsysTableMasterSlave(QolsysTable):

    def __init__(self,db:sqlite3.Connection,cursor:sqlite3.Cursor) -> None:
        super().__init__(db,cursor)
        self._uri = "content://com.qolsys.qolsysprovider.MasterSlaveContentProvider/master_slave"
        self._table = "master_slave"
        self._abort_on_error = False

        self._columns = [
            "_id",
            "version",
            "opr",
            "partition_id",
            "zone_id",
            "ip_address",
            "mac_address",
            "device_type",
            "created_by",
            "created_date",
            "updated_by",
            "last_updated_date",
            "status",
            "device_name",
            "last_updated_iq_remote_checksum",
            "software_version",
            "upgrade_status",
            "name",
            "bssid",
            "dhcpInfo",
            "topology",
            "reboot_reason",
        ]

        self._create_table()

    def insert(self, data:dict) -> None:
        self._cursor.execute(f"INSERT INTO {self.table} (_id,version,opr,partition_id,zone_id,ip_address,mac_address,device_type,created_by,created_date,updated_by,last_updated_date,status,device_name,last_updated_iq_remote_checksum,software_version,upgrade_status,name,bssid,dhcpInfo,topology) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(
            data.get("_id"),
            data.get("version",""),
            data.get("opr",""),
            data.get("partition_id",""),
            data.get("zone_id",""),
            data.get("ip_address",""),
            data.get("mac_address",""),
            data.get("device_type",""),
            data.get("created_by",""),
            data.get("created_date",""),
            data.get("updated_by",""),
            data.get("last_updated_date",""),
            data.get("status",""),
            data.get("device_name",""),
            data.get("last_updated_iq_remote_checksum",""),
            data.get("software_version",""),
            data.get("upgrade_status",""),
            data.get("name",""),
            data.get("bssid",""),
            data.get("dhcpInfo",""),
            data.get("topology","")))

        self._db.commit()

