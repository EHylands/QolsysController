import logging  # noqa: INP001
import sqlite3

from .table import QolsysTable
from .table_alarmedsensor import QolsysTableAlarmedSensor
from .table_automation import QolsysTableAutomation
from .table_country_locale import QolsysTableCountryLocale
from .table_dashboard_msgs import QolsysTableDashboardMsgs
from .table_dimmerlight import QolsysTableDimmerLight
from .table_doorlock import QolsysTableDoorLock
from .table_eu_event import QolsysTableEuEvent
from .table_heat_map import QolsysTableHeatMap
from .table_history import QolsysTableHistory
from .table_iqremotesettings import QolsysTableIqRemoteSettings
from .table_iqrouter_network_config import QolsysTableIqRouterNetworkConfig
from .table_iqrouter_user_device import QolsysTableIqRouterUserDevice
from .table_master_slave import QolsysTableMasterSlave
from .table_partition import QolsysTablePartition
from .table_powerg_device import QolsysTablePowerGDevice
from .table_qolsyssettings import QolsysTableQolsysSettings
from .table_scene import QolsysTableScene
from .table_sensor import QolsysTableSensor
from .table_smartsocket import QolsysTableSmartSocket
from .table_state import QolsysTableState
from .table_tcc import QolsysTableTcc
from .table_thermostat import QolsysTableThermostat
from .table_trouble_conditions import QolsysTableTroubleConditions
from .table_user import QolsysTableUser
from .table_virtual_device import QolsysTableVirtualDevice
from .table_weather import QolsysTableWeather
from .table_zigbee_device import QolsysTableZigbeeDevice
from .table_zwave_association_group import QolsysTableZwaveAssociationGroup
from .table_zwave_history import QolsysTableZwaveHistory
from .table_zwave_node import QolsysTableZwaveNode
from .table_zwave_other import QolsysTableZwaveOther

LOGGER = logging.getLogger(__name__)

class QolsysDB:

    def __init__(self) -> None:  # noqa: PLR0915

        self._db:sqlite3.Connection = sqlite3.connect(":memory:")
        self._cursor:sqlite3.Cursor = self._db.cursor()

        self.table_alarmedsensor = QolsysTableAlarmedSensor(self.db,self.cursor)
        self.table_automation = QolsysTableAutomation(self.db,self.cursor)
        self.table_country_locale = QolsysTableCountryLocale(self.db,self.cursor)
        self.table_dashboard_msgs = QolsysTableDashboardMsgs(self.db,self.cursor)
        self.table_dimmer = QolsysTableDimmerLight(self.db,self.cursor)
        self.table_doorlock = QolsysTableDoorLock(self.db,self.cursor)
        self.table_eu_event = QolsysTableEuEvent(self.db,self.cursor)
        self.table_heat_map = QolsysTableHeatMap(self.db,self.cursor)
        self.table_history = QolsysTableHistory(self.db,self.cursor)
        self.table_iqremotesettings = QolsysTableIqRemoteSettings(self.db,self.cursor)
        self.table_iqrouter_network_config = QolsysTableIqRouterNetworkConfig(self.db,self.cursor)
        self.table_iqrouter_user_device = QolsysTableIqRouterUserDevice(self.db,self.cursor)
        self.table_master_slave = QolsysTableMasterSlave(self.db,self.cursor)
        self.table_partition = QolsysTablePartition(self.db,self.cursor)
        self.table_powerg_device = QolsysTablePowerGDevice(self.db,self.cursor)
        self.table_sensor = QolsysTableSensor(self.db,self.cursor)
        self.table_smartsocket = QolsysTableSmartSocket(self.db,self.cursor)
        self.table_qolsyssettings = QolsysTableQolsysSettings(self.db,self.cursor)
        self.table_scene = QolsysTableScene(self.db,self.cursor)
        self.table_state = QolsysTableState(self.db,self.cursor)
        self.table_tcc = QolsysTableTcc(self.db,self.cursor)
        self.table_thermostat = QolsysTableThermostat(self.db,self.cursor)
        self.table_trouble_conditions = QolsysTableTroubleConditions(self.db,self.cursor)
        self.table_user = QolsysTableUser(self.db,self.cursor)
        self.table_virtual_device = QolsysTableVirtualDevice(self.db,self.cursor)
        self.table_weather = QolsysTableWeather(self.db,self.cursor)
        self.table_zigbee_device = QolsysTableZigbeeDevice(self.db,self.cursor)
        self.table_zwave_association_goup = QolsysTableZwaveAssociationGroup(self.db,self.cursor)
        self.table_zwave_history = QolsysTableZwaveHistory(self.db,self.cursor)
        self.table_zwave_node = QolsysTableZwaveNode(self.db,self.cursor)
        self.table_zwave_other = QolsysTableZwaveOther(self.db,self.cursor)

        self._table_array = []
        self._table_array.append(self.table_sensor)
        self._table_array.append(self.table_partition)
        self._table_array.append(self.table_qolsyssettings)
        self._table_array.append(self.table_alarmedsensor)
        self._table_array.append(self.table_state)
        self._table_array.append(self.table_history)
        self._table_array.append(self.table_zwave_node)
        self._table_array.append(self.table_zwave_history)
        self._table_array.append(self.table_iqremotesettings)
        self._table_array.append(self.table_iqrouter_network_config)
        self._table_array.append(self.table_iqrouter_user_device)
        self._table_array.append(self.table_thermostat)
        self._table_array.append(self.table_dimmer)
        self._table_array.append(self.table_doorlock)
        self._table_array.append(self.table_smartsocket)
        self._table_array.append(self.table_automation)
        self._table_array.append(self.table_dashboard_msgs)
        self._table_array.append(self.table_heat_map)
        self._table_array.append(self.table_master_slave)
        self._table_array.append(self.table_scene)
        self._table_array.append(self.table_user)
        self._table_array.append(self.table_country_locale)
        self._table_array.append(self.table_zwave_other)
        self._table_array.append(self.table_tcc)
        self._table_array.append(self.table_weather)
        self._table_array.append(self.table_powerg_device)
        self._table_array.append(self.table_trouble_conditions)
        self._table_array.append(self.table_zigbee_device)
        self._table_array.append(self.table_zwave_association_goup)
        self._table_array.append(self.table_virtual_device)
        self._table_array.append(self.table_eu_event)

        # Other Table not Implemented
        # content://com.qolsys.qolsysprovider.AllSensorsContentProvider/all_sensor
        # content://com.qolsys.qolsysprovider.CameraRequestContentProvider/camerarequest
        # content://com.qolsys.qolsysprovider.FAQContentProvider/faq
        # content://com.qolsys.qolsysprovider.HomeAutomationEventsContentProvider/home_automation_event
        # content://com.qolsys.qolsysprovider.HomeAutomationPendingContentProvider/home_automation_pending
        # content://com.qolsys.qolsysprovider.HomeAutomationRulesContentProvider/home_automation_rule
        # content://com.qolsys.qolsysprovider.ZigbeeSmartEnergyContentProvider/zigbee_smart_energy
        # content://com.qolsys.qolsysprovider.ProvisionListContentProvider/provision_list
        # content://com.qolsys.qolsysprovider.PowerGSignalStrengthContentProvider/powerg_signal_strength
        # content://com.qolsys.qolsysprovider.ProximityTagContentProvider/proximity_tag
        # content://com.qolsys.qolsysprovider.OutputRulesContentProvider/output_rules
        # content://com.qolsys.qolsysprovider.IQCameraContentProvider/iqcamera
        # content://com.qolsys.qolsysprovider.CorbusDeviceContentProvider/corbus_device
        # content://com.qolsys.qolsysprovider.AutomationRulesContentProvider/automation_rules
        # content://com.qolsys.qolsysprovider.WifiClientsContentProvider/wifi_clients_table
        # content://com.qolsys.qolsysprovider.MxLoopControllerContentProvider/mx_loop_controller
        # content://com.qolsys.qolsysprovider.SystemCheckContentProvider/system_check
        # content://com.qolsys.qolsysprovider.BluetoothDevicesContentProvider/bluetooth_devices
        # content://com.qolsys.qolsysprovider.AxonDeviceContentProvider/axon_device
        # content://com.qolsys.qolsysprovider.AxonSignalStrengthContentProvider/axon_signal_strength
        # content://com.qolsys.qolsysprovider.PanelInfoContentProvider/panel_info
        # content://com.qolsys.qolsysprovider.AxonRSSIContentProvider/axon_rssi_table
        # content://com.qolsys.qolsysprovider.PowerGDeviceContentProvider/powerg_device
        # content://com.qolsys.qolsysprovider.PowerGRSSIContentProvider/powerg_rssi_table

    @property
    def db(self) -> sqlite3.Connection:
        return self._db

    @property
    def cursor(self) -> sqlite3.Cursor:
        return self._cursor

    def get_partitions(self) -> list[dict]:
        self.cursor.execute(f"SELECT * FROM {self.table_partition.table} ORDER BY partition_id" )
        self.db.commit()

        partitions = []
        columns = [description[0] for description in self.cursor.description]
        for row in  self.cursor.fetchall():
            row_dict = dict(zip(columns, row, strict=True))
            partitions.append(row_dict)

        return partitions

    def get_zwave_devices(self) -> list[dict]:
        self.cursor.execute(f"SELECT * FROM {self.table_zwave_node.table} ORDER BY node_id" )
        self.db.commit()

        devices = []
        columns = [description[0] for description in self.cursor.description]
        for row in  self.cursor.fetchall():
            row_dict = dict(zip(columns, row, strict=True))
            devices.append(row_dict)

        return devices

    def get_locks(self) -> list[dict]:
        self.cursor.execute(f"SELECT * FROM {self.table_doorlock.table} ORDER BY node_id" )
        self.db.commit()

        locks = []
        columns = [description[0] for description in self.cursor.description]
        for row in  self.cursor.fetchall():
            row_dict = dict(zip(columns, row, strict=True))
            locks.append(row_dict)

        return locks

    def get_thermostats(self) -> list[dict]:
        self.cursor.execute(f"SELECT * FROM {self.table_thermostat.table} ORDER BY node_id" )
        self.db.commit()

        thermostats = []
        columns = [description[0] for description in self.cursor.description]
        for row in  self.cursor.fetchall():
            row_dict = dict(zip(columns, row, strict=True))
            thermostats.append(row_dict)

        return thermostats

    def get_dimmers(self) -> list[dict]:
        self.cursor.execute(f"SELECT * FROM {self.table_dimmer.table} ORDER BY node_id" )
        self.db.commit()

        dimmers = []
        columns = [description[0] for description in self.cursor.description]
        for row in  self.cursor.fetchall():
            row_dict = dict(zip(columns, row, strict=True))
            dimmers.append(row_dict)

        return dimmers

    def get_zones(self) -> list[dict]:
        self.cursor.execute(f"SELECT * FROM {self.table_sensor.table} ORDER BY zoneid" )
        self.db.commit()

        zones = []
        columns = [description[0] for description in self.cursor.description]
        for row in  self.cursor.fetchall():
            row_dict = dict(zip(columns, row, strict=True))
            zones.append(row_dict)

        return zones

    def get_setting_panel(self,setting:str) -> str:
        self.cursor.execute(f"SELECT value FROM {self.table_qolsyssettings.table} WHERE name = ? and partition_id  = ? ", (setting,"0"))
        row = self.cursor.fetchone()

        if row is None:
            LOGGER.debug("%s value not found",setting)
            return None

        return row[0]

    def get_setting_partition(self,setting:str,partition_id:str) -> str | None:
        self.cursor.execute(f"SELECT value FROM {self.table_qolsyssettings.table} WHERE name = ? and partition_id  = ? ", (setting,partition_id))
        row = self.cursor.fetchone()

        if row is None:
            LOGGER.debug("%s value not found",setting)
            return None

        return row[0]

    def get_state_partition(self,state:str,partition_id:str) -> str | None:
        self.cursor.execute(f"SELECT value FROM {self.table_state.table} WHERE name = ? and partition_id  = ? ", (state,partition_id))
        row = self.cursor.fetchone()

        if row is None:
            LOGGER.debug("%s value not found",state)
            return None

        return row[0]

    def get_alarm_type(self,partition_id:str) -> list[str]:
        alarm_type = []
        self.cursor.execute(f"SELECT sgroup FROM {self.table_alarmedsensor.table} WHERE partition_id  = ? ", (partition_id))
        rows = self.cursor.fetchall()

        for row in rows:
            alarm_type.append(row[0])

        return alarm_type

    def clear_db(self) -> None:
        for table in self._table_array:
            table.clear()

    def get_table(self,uri:str) -> QolsysTable | None:
        for table in self._table_array:
            if uri == table.uri:
                return table

        return None

    def load_db(self,database:dict) -> None:

        self.clear_db()

        if not database:
            LOGGER.error("Loading Database Error, No Data Provided")
            return

        for uri in database:
            table = self.get_table(uri.get("uri"))

            if table is None:
                LOGGER.error("Please Report")
                LOGGER.error("Loading Unknown databse URI")
                LOGGER.error(uri)
                continue

            for u in uri.get("resultSet"):
                table.insert(data=u)
