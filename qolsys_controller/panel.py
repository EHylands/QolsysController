import json
import logging
from datetime import datetime
from pathlib import Path

from .database.db import QolsysDB
from .enum import (
    PartitionAlarmState,
    PartitionAlarmType,
    PartitionSystemStatus,
)
from .observable import QolsysObservable
from .partition import QolsysPartition
from .state import QolsysState
from .zone import QolsysZone
from .zwave_device import QolsysZWaveDevice
from .zwave_dimmer import QolsysDimmer
from .zwave_generic import QolsysGeneric
from .zwave_lock import QolsysLock
from .zwave_thermostat import QolsysThermostat

LOGGER = logging.getLogger(__name__)

class QolsysPanel(QolsysObservable):
    def __init__(self,settings_directory:str,state:QolsysState) -> None:

        self._state = state
        self._db = QolsysDB()

        # Partition settings
        self.settings_partition = ["SYSTEM_STATUS","EXIT_SOUNDS","ENTRY_DELAYS","SYSTEM_STATUS_CHANGED_TIME"]
        self.state_partition = ["ALARM_STATE"]

        # Panel settings
        self.settings_panel_observer = QolsysObservable()
        self.settings_panel = ["PANEL_TAMPER_STATE","AC_STATUS","BATTERY_STATUS","FAIL_TO_COMMUNICATE","SECURE_ARMING",
                                "AUTO_BYPASS","AUTO_STAY","AUTO_ARM_STAY","AUTO_EXIT_EXTENSION","FINAL_EXIT_DOOR_ARMING"
                                "NO_ARM_LOW_BATTERY","TEMPFORMAT","LANGUAGE","COUNTRY","SYSTEM_TIME","GSM_CONNECTION_STATUS",
                                "GSM_SIGNAL_STRENGTH","ANDROID_VERSION","HARDWARE_VERSION","TIMER_NORMAL_ENTRY_DELAY",
                                "TIMER_NORMAL_EXIT_DELAY","TIMER_LONG_ENTRY_DELAY","TIMER_LONG_EXIT_DELAY","ZWAVE_CONTROLLER",
                                "ZWAVE_CARD","POLICE_PANIC_ENABLED","FIRE_PANIC_ENABLED","AUXILIARY_PANIC_ENABLED","NIGHTMODE_SETTINGS",
                                "NIGHT_SETTINGS_STATE","PARTITIONS","SIX_DIGIT_USER_CODE","SHOW_SECURITY_SENSORS","SYSTEM_LOGGED_IN_USER",
                                "PANEL_SCENES_SETTING","CONTROL_4","ZWAVE_FIRM_WARE_VERSION","FINAL_EXIT_DOOR_ARMING","NO_ARM_LOW_BATTERY","MAC_ADDRESS","LAST_UPDATE_IQ_REMOTE_PATCH_CKECKSUM_N" ]

        self._PANEL_TAMPER_STATE = ""
        self._AC_STATUS = ""
        self._BATTERY_STATUS = ""
        self._FAIL_TO_COMMUNICATE = ""
        self._SECURE_ARMING = ""
        self._AUTO_BYPASS = ""
        self._AUTO_STAY = ""
        self._AUTO_ARM_STAY = ""
        self._AUTO_EXIT_EXTENSION = ""
        self._FINAL_EXIT_DOOR_ARMING = ""
        self._NO_ARM_LOW_BATTERY = ""
        self._TEMPFORMAT = ""
        self._LANGUAGE = ""
        self._COUNTRY = ""
        self._SYSTEM_TIME = ""
        self._GSM_CONNECTION_STATUS = ""
        self._GSM_SIGNAL_STRENGTH = ""
        self._ANDROID_VERSION = ""
        self._HARDWARE_VERSION = ""
        self._TIMER_NORMAL_ENTRY_DELAY = ""
        self._TIMER_NORMAL_EXIT_DELAY = ""
        self._TIMER_LONG_ENTRY_DELAY = ""
        self._TIMER_LONG_EXIT_DELAY = ""
        self._ZWAVE_FIRM_WARE_VERSION = ""
        self._ZWAVE_CONTROLLER = ""
        self._ZWAVE_CARD = ""
        self._POLICE_PANIC_ENABLED = ""
        self._FIRE_PANIC_ENABLED = ""
        self._AUXILIARY_PANIC_ENABfLED = ""
        self._NIGHTMODE_SETTINGS = ""
        self._NIGHT_SETTINGS_STATE = ""
        self._PARTITIONS = ""
        self._SIX_DIGIT_USER_CODE = ""
        self._SHOW_SECURITY_SENSORS = ""
        self._CONTROL_4 = ""
        self._MAC_ADDRESS = ""
        self._SYSTEM_LOGGED_IN_USER = ""
        self._PANEL_SCENES_SETTING = ""
        self._LAST_UPDATE_IQ_REMOTE_PATCH_CKECKSUM_N = ""

        self._users = []
        self._unique_id = ""
        self._settings_directory = settings_directory

        self._imei = ""
        self._product_type = ""

    def read_users_file(self) -> bool:
        # Loading user_code data from users.conf file
        try:
            path = Path(self._settings_directory + "users.conf")
            with path.open("r", encoding="utf-8") as file:
                try:
                    users = json.load(file)
                    for user in users:
                        self._users.append(user)

                except json.JSONDecodeError:
                    LOGGER.exception("users.conf file json error")
                    return False

        except FileNotFoundError:
            LOGGER.exception("users.conf file not found")
            return False

        return True

    @property
    def db(self) -> QolsysDB:
        return self._db

    @property
    def ANDROID_VERSION(self) -> str:
        self._ANDROID_VERSION = self.db.get_setting_panel("ANDROID_VERSION")
        return self._ANDROID_VERSION

    @property
    def PANEL_TAMPER_STATE(self) -> str:
        self._PANEL_TAMPER_STATE = self.db.get_setting_panel("PANEL_TAMPER_STATE")
        return self._PANEL_TAMPER_STATE

    @property
    def AC_STATUS(self) -> str:
        self._AC_STATUS = self.db.get_setting_panel("AC_STATUS")
        return self._AC_STATUS

    @property
    def BATTERY_STATUS(self) -> str:
        self._BATTERY_STATUS = self.db.get_setting_panel("BATTERY_STATUS")
        return self._BATTERY_STATUS

    @property
    def FAIL_TO_COMMUNICATE(self) -> str:
        self._FAIL_TO_COMMUNICATE = self.db.get_setting_panel("FAIL_TO_COMMUNICATE")
        return self._FAIL_TO_COMMUNICATE

    @property
    def SECURE_ARMING(self) -> str:
        self._SECURE_ARMING = self.db.get_setting_panel("SECURE_ARMING")
        return self._SECURE_ARMING

    @property
    def AUTO_BYPASS(self) -> str:
        self._AUTO_BYPASS = self.db.get_setting_panel("AUTO_BYPASS")
        return self._AUTO_BYPASS

    @property
    def AUTO_STAY(self) -> str:
        self._AUTO_STAY = self.db.get_setting_panel("AUTO_STAY")
        return self._AUTO_STAY

    @property
    def AUTO_ARM_STAY(self) -> str:
        self._AUTO_ARM_STAY = self.db.get_setting_panel("AUTO_ARM_STAY")
        return self._AUTO_ARM_STAY

    @property
    def AUTO_EXIT_EXTENSION(self) -> str:
        self._AUTO_EXIT_EXTENSION = self.db.get_setting_panel("AUTO_EXIT_EXTENSION")
        return self._AUTO_EXIT_EXTENSION

    @property
    def FINAL_EXIT_DOOR_ARMING(self) -> str:
        self._FINAL_EXIT_DOOR_ARMING = self.db.get_setting_panel("FINAL_EXIT_DOOR_ARMING")
        return self._FINAL_EXIT_DOOR_ARMING

    @property
    def NO_ARM_LOW_BATTERY(self) -> str:
        self._NO_ARM_LOW_BATTERY = self.db.get_setting_panel("NO_ARM_LOW_BATTERY")
        return self._NO_ARM_LOW_BATTERY

    @property
    def TEMPFORMAT(self) -> str:
        self._TEMPFORMAT = self.db.get_setting_panel("TEMPFORMAT")
        return self._TEMPFORMAT

    @property
    def LANGUAGE(self) -> str:
        self._LANGUAGE = self.db.get_setting_panel("LANGUAGE")
        return self._LANGUAGE

    @property
    def COUNTRY(self) -> str:
        self._COUNTRY = self.db.get_setting_panel("COUNTRY")
        return self._COUNTRY

    @property
    def SYSTEM_TIME(self) -> str:
        self._SYSTEM_TIME = self.db.get_setting_panel("SYSTEM_TIME")
        return self._SYSTEM_TIME

    @property
    def GSM_CONNECTION_STATUS(self) -> str:
        self._GSM_CONNECTION_STATUS = self.db.get_setting_panel("GSM_CONNECTION_STATUS")
        return self._GSM_CONNECTION_STATUS

    @property
    def GSM_SIGNAL_STRENGTH(self) -> str:
        self._GSM_SIGNAL_STRENGTH = self.db.get_setting_panel("GSM_SIGNAL_STRENGTH")
        return self._GSM_SIGNAL_STRENGTH

    @property
    def HARDWARE_VERSION(self) -> str:
        self._HARDWARE_VERSION = self.db.get_setting_panel("HARDWARE_VERSION")
        return self._HARDWARE_VERSION

    @property
    def ZWAVE_FIRM_WARE_VERSION(self) -> str:
        self._ZWAVE_FIRM_WARE_VERSION = self.db.get_setting_panel("ZWAVE_FIRM_WARE_VERSION")
        return self._ZWAVE_FIRM_WARE_VERSION

    @property
    def ZWAVE_CONTROLLER(self) -> str:
        self._ZWAVE_CONTROLLER = self.db.get_setting_panel("ZWAVE_CONTROLLER")
        return self._ZWAVE_CONTROLLER

    @property
    def ZWAVE_CARD(self) -> str:
        self._ZWAVE_CARD = self.db.get_setting_panel("ZWAVE_CARD")
        return self._ZWAVE_CARD

    @property
    def POLICE_PANIC_ENABLED(self) -> str:
        self._POLICE_PANIC_ENABLED = self.db.get_setting_panel("POLICE_PANIC_ENABLED")
        return self._POLICE_PANIC_ENABLED

    @property
    def FIRE_PANIC_ENABLED(self) -> str:
        self._FIRE_PANIC_ENABLED = self.db.get_setting_panel("FIRE_PANIC_ENABLED")
        return self._FIRE_PANIC_ENABLED

    @property
    def AUXILIARY_PANIC_ENABLED(self) -> str:
        self._AUXILIARY_PANIC_ENABLED = self.db.get_setting_panel("AUXILIARY_PANIC_ENABLED")
        return self._AUXILIARY_PANIC_ENABLED

    @property
    def PARTITIONS(self) -> str:
        self._PARTITIONS = self.db.get_setting_panel("PARTITIONS")
        return self._PARTITIONS

    @property
    def SIX_DIGIT_USER_CODE(self) -> str:
        self._SIX_DIGIT_USER_CODE = self.db.get_setting_panel("SIX_DIGIT_USER_CODE")
        return self._SIX_DIGIT_USER_CODE

    @property
    def CONTROL_4(self) -> str:
        self._CONTROL_4 = self.db.get_setting_panel("CONTROL_4")
        return self._CONTROL_4

    @property
    def NIGHTMODE_SETTINGS(self) -> str:
        self._NIGHTMODE_SETTINGS = self.db.get_setting_panel("NIGHTMODE_SETTINGS")
        return self._NIGHTMODE_SETTINGS

    @property
    def NIGHT_SETTINGS_STATE(self) -> str:
        self._NIGHT_SETTINGS_STATE = self.db.get_setting_panel("NIGHT_SETTINGS_STATE")
        return self._NIGHT_SETTINGS_STATE

    @property
    def SHOW_SECURITY_SENSORS(self) -> str:
        self._SHOW_SECURITY_SENSORS = self.db.get_setting_panel("SHOW_SECURITY_SENSORS")
        return self._SHOW_SECURITY_SENSORS

    @property
    def TIMER_NORMAL_ENTRY_DELAY(self) -> str:
        self._TIMER_NORMAL_ENTRY_DELAY = self.db.get_setting_panel("TIMER_NORMAL_ENTRY_DELAY")
        return self._TIMER_NORMAL_ENTRY_DELAY

    @property
    def TIMER_NORMAL_EXIT_DELAY(self) -> str:
        self._TIMER_NORMAL_EXIT_DELAY = self.db.get_setting_panel("TIMER_NORMAL_EXIT_DELAY")
        return self._TIMER_NORMAL_EXIT_DELAY

    @property
    def TIMER_LONG_ENTRY_DELAY(self) -> str:
        self._TIMER_LONG_ENTRY_DELAY = self.db.get_setting_panel("TIMER_LONG_ENTRY_DELAY")
        return self._TIMER_LONG_ENTRY_DELAY

    @property
    def  MAC_ADDRESS(self) -> str:
        self._MAC_ADDRESS = self.db.get_setting_panel("MAC_ADDRESS")
        return self._MAC_ADDRESS

    @MAC_ADDRESS.setter
    def MAC_ADDRESS(self, value:str) -> None:
        self._MAC_ADDRESS = value

    @property
    def unique_id(self)  -> str:
        mac_address = self.MAC_ADDRESS
        return mac_address.replace(":","")

    @property
    def TIMER_LONG_EXIT_DELAY(self) ->  str:
        self._TIMER_LONG_EXIT_DELAY = self.db.get_setting_panel("TIMER_LONG_ENTRY_DELAY")
        return self._TIMER_LONG_EXIT_DELAY

    @property
    def LAST_UPDATE_IQ_REMOTE_PATCH_CKECKSUM_N(self) -> str :
        self._LAST_UPDATE_IQ_REMOTE_PATCH_CKECKSUM_N = self.db.get_setting_panel("LAST_UPDATE_IQ_REMOTE_PATCH_CKECKSUM_N")
        return self._LAST_UPDATE_IQ_REMOTE_PATCH_CKECKSUM_N

    @property
    def imei(self) -> str:
        return self._imei

    @imei.setter
    def imei(self,value:str) -> None:
        self._imei = value

    @property
    def product_type(self) -> str:
        return self._product_type

    @product_type.setter
    def product_type(self,value:str) -> None:
        self._product_type = value

    @property
    def SYSTEM_LOGGED_IN_USER(self) -> str:
        self._SYSTEM_LOGGED_IN_USER = self.db.get_setting_panel("SYSTEM_LOGGED_IN_USER")
        return self._SYSTEM_LOGGED_IN_USER

    @SYSTEM_LOGGED_IN_USER.setter
    def SYSTEM_LOGGED_IN_USER(self,value:str) -> None:
        self._SYSTEM_LOGGED_IN_USER = value

    @property
    def PANEL_SCENES_SETTING(self) -> str:
        self._PANEL_SCENES_SETTING = self.db.get_setting_panel("PANEL_SCENES_SETTING")
        return self.PANEL_SCENES_SETTING

    def load_database(self,database:dict) -> None:
        self.db.load_db(database)
        self._state.sync_partitions_data(self.get_partitions_from_db())
        self._state.sync_zones_data(self.get_zones_from_db())
        self._state.sync_zwave_devices_data(self.get_zwave_devices_from_db())

    # Parse panel update to database
    def parse_iq2meid_message(self,data:dict) -> bool:  # noqa: C901, PLR0912, PLR0915

        eventName = data.get("eventName")
        dbOperation = data.get("dbOperation")
        uri = data.get("uri")

        match eventName:

            case "stopScreenCapture":
                pass

            case "dbChanged":

                match dbOperation:

                    case "update":
                        content_values = data.get("contentValues")
                        selection = data.get("selection")
                        selection_argument = data.get("selectionArgs")

                        match uri:

                            # Update Settings Content Provider
                            case self.db.table_qolsyssettings.uri:
                                name = content_values.get("name","")
                                new_value = content_values.get("value","")
                                old_value = self.db.get_setting_panel(name)
                                self.db.table_qolsyssettings.update(selection,selection_argument,content_values)

                                # Update Panel Settings - Send notification if settings ha changed
                                if name in self.settings_panel and old_value != new_value:
                                    LOGGER.debug("Panel Setting - %s: %s",name,new_value)
                                    self.settings_panel_observer.notify()

                                # Update Partition setting - Send notification if setting has changed
                                if name in self.settings_partition:
                                    partition_id = content_values.get("partition_id","")
                                    partition = self._state.partition(partition_id)
                                    if partition is not None:
                                       match name:
                                            case "SYSTEM_STATUS":
                                                partition.system_status = PartitionSystemStatus(new_value)
                                            case "SYSTEM_STATUS_CHANGED_TIME":
                                                partition.system_status_changed_time = new_value
                                            case "EXIT_SOUNDS":
                                                partition.exit_sounds = new_value
                                            case "ENTRY_DELAYS":
                                                partition.entry_delays = new_value

                            # Update Sensor Content Provider
                            case self.db.table_sensor.uri:
                                self.db.table_sensor.update(selection,selection_argument,content_values)
                                zoneid =  content_values.get("zoneid","")
                                zone = self._state.zone(zoneid)
                                if zone is not None:
                                    zone.update(content_values)

                            # Update State
                            case self.db.table_state.uri:
                                name = content_values.get("name","")
                                new_value = content_values.get("value","")
                                partition_id = content_values.get("partition_id","")
                                self.db.table_state.update(selection,selection_argument,content_values)

                                if name in self.state_partition:
                                    partition = self._state.partition(partition_id)
                                    if partition is not None:
                                        match name:
                                            case "ALARM_STATE":
                                                partition.alarm_state = PartitionAlarmState(new_value)

                            # Update heat_map
                            case self.db.table_heat_map.uri:
                                self.db.table_heat_map.update(selection,selection_argument,content_values)
                                # No action needed

                            # Update master_slave
                            case self.db.table_master_slave.uri:
                                self.db.table_master_slave.update(selection,selection_argument,content_values)
                                # No action needed

                            # Update dashboard_msgs
                            case self.db.table_dashboard_msgs.uri:
                                self.db.table_dashboard_msgs.update(selection,selection_argument,content_values)
                                # No action needed

                            # Update PartitionContentProvider
                            case self.db.table_partition.uri:
                                self.db.table_partition.update(selection,selection_argument,content_values)
                                partition_id = content_values.get("partition_id","")
                                partition = self._state.partition(partition_id)
                                if partition is not None:
                                    partition.update_partition(content_values)

                            # Update History Content Provider
                            case self.db.table_history.uri:
                                self.db.table_history.update(selection,selection_argument,content_values)
                                # No action needed

                            # Update DimmerLightsContentProvider
                            case self.db.table_dimmer.uri:
                                self.db.table_dimmer.update(selection,selection_argument,content_values)
                                node_id =  content_values.get("node_id","")
                                node = self._state.zwave_device(node_id)
                                if node is not None and isinstance(node,QolsysDimmer):
                                    node.update_dimmer(content_values)

                            # Update Thermostat Content Provider
                            case self.db.table_thermostat.uri:
                                self.db.table_thermostat.update(selection,selection_argument,content_values)
                                node_id =  content_values.get("node_id","")
                                node = self._state.zwave_device(node_id)
                                if node is not None and isinstance(node,QolsysThermostat):
                                    node.update_thermostat(content_values)

                            # Update DoorLockContentProvider
                            case self.db.table_doorlock.uri:
                                self.db.table_doorlock.update(selection,selection_argument,content_values)
                                node_id =  content_values.get("node_id","")
                                node = self._state.zwave_device(node_id)
                                if node is not None and isinstance(node,QolsysLock):
                                    node.update_lock(content_values)

                            # Update ZwaveContentProvider
                            case self.db.table_zwave_node.uri:
                                self.db.table_zwave_node.update(selection,selection_argument,content_values)
                                node_id =  content_values.get("node_id","")
                                node = self._state.zwave_device(node_id)
                                if node is not None:
                                    node.update_base(content_values)

                            # Update Z-Wave History Content Provier
                            case self.db.table_zwave_history.uri:
                                self.db.table_zwave_history.update(selection,selection_argument,content_values)
                                # No action needed

                            # Update AutomationDeviceContentProvider
                            case self.db.table_automation.uri:
                                self.db.table_automation.update(selection,selection_argument,content_values)
                                # No action needed

                            # Update Alarmed Sensor Content Provider
                            case self.db.table_alarmedsensor.uri:
                                self.db.table_alarmedsensor.update(selection,selection_argument,content_values)

                            # Update IQ Remote Settings Content Provider
                            case self.db.table_iqremotesettings.uri:
                                self.db.table_iqremotesettings.update(selection,selection_argument,content_values)
                                # No action needed

                            case _:
                                LOGGER.debug("iq2meid updating unknow uri:%s",uri)
                                LOGGER.debug(data)

                    case "delete":
                        selection = data.get("selection")
                        selection_argument = data.get("selectionArgs")

                        match uri:

                            case self.db.table_sensor.uri:
                                self.db.table_sensor.delete(selection,selection_argument)
                                self._state.sync_zones_data(self.get_zones_from_db())
                                # Notify delete zone

                            case self.db.table_iqremotesettings.uri:
                                self.db.table_iqremotesettings.delete(selection,selection_argument)
                                # No action needed

                            case self.db.table_state.uri:
                                self.db.table_state.delete(selection,selection_argument)
                                # No action needed

                            case self.db.table_master_slave.uri:
                                self.db.table_master_slave.delete(selection,selection_argument)
                                # No action needed

                            case self.db.table_qolsyssettings.uri:
                                self.db.table_qolsyssettings.delete(selection,selection_argument)
                                # No action needed

                            case self.db.table_alarmedsensor.uri:
                                self.db.table_alarmedsensor.delete(selection,selection_argument)
                                self._state.sync_partitions_data(self.get_partitions_from_db())

                            case self.db.table_history.uri:
                                self.db.table_history.delete(selection,selection_argument)
                                # No action needed

                            case self.db.table_zwave_history.uri:
                                self.db.table_zwave_history.delete(selection,selection_argument)
                                # No action needed

                            case self.db.table_doorlock.uri:
                                self.db.table_doorlock.delete(selection,selection_argument)
                                self._state.sync_zwave_devices_data(self.get_zwave_devices_from_db())

                            case self.db.table_dimmer.uri:
                                self.db.table_dimmer.delete(selection,selection_argument)
                                self._state.sync_zwave_devices_data(self.get_zwave_devices_from_db())

                            case self.db.table_thermostat.uri:
                                self.db.table_thermostat.delete(selection,selection_argument)
                                self._state.sync_zwave_devices_data(self.get_zwave_devices_from_db())

                            case self.db.table_zwave_node.uri:
                                self.db.table_zwave_node.delete(selection,selection_argument)
                                self._state.sync_zwave_devices_data(self.get_zwave_devices_from_db())

                            case self.db.table_automation.uri:
                                self.db.table_automation.delete(selection,selection_argument)
                                # No action needed

                            case self.db.table_partition.uri:
                                self.db.table_partition.delete(selection,selection_argument)
                                self._state.sync_partitions_data(self.get_partitions_from_db())

                            case self.db.table_user.uri:
                                self.db.table_user.delete(selection,selection_argument)
                                # No action needed

                            case self.db.table_dashboard_msgs.uri:
                                self.db.table_dashboard_msgs.delete(selection,selection_argument)
                                # No action needed

                            case _:
                                LOGGER.debug("iq2meid deleting unknown uri:%s",uri)
                                LOGGER.debug(data)

                    case "insert":
                        content_values = data.get("contentValues")

                        match uri:

                            # Inser State Content Provider
                            case self.db.table_state.uri:
                                self.db.table_state.insert(data=content_values)

                                name = content_values.get("name","")
                                new_value = content_values.get("value","")
                                if name in self.state_partition:
                                    partition_id = content_values.get("partition_id","")
                                    partition = self._state.partition(partition_id)
                                    if partition is not None:
                                        match name:
                                            case "ALARM_STATE":
                                                partition.alarm_state = PartitionAlarmState(new_value)

                            # Inser Partition Content Provider
                            case self.db.table_partition:
                                self.db.table_partition.insert(data=content_values)
                                self._state.sync_partitions_data(self.get_partitions_from_db())

                            # Insert Settings Content Provider
                            case self.db.table_qolsyssettings.uri:
                                self.db.table_qolsyssettings.insert(data=content_values)

                                # Update Partition setting - Send notification if setting has changed
                                name = content_values.get("name","")
                                new_value = content_values.get("value","")
                                if name in self.settings_partition:
                                    partition_id = content_values.get("partition_id","")
                                    partition = self._state.partition(partition_id)
                                    if partition is not None:
                                       match name:
                                            case "SYSTEM_STATUS":
                                                partition.system_status = PartitionSystemStatus(new_value)
                                            case "SYSTEM_STATUS_CHANGED_TIME":
                                                partition.system_status_changed_time = new_value
                                            case "EXIT_SOUNDS":
                                                partition.exit_sounds = new_value
                                            case "ENTRY_DELAYS":
                                                partition.entry_delays = new_value

                            # UserContentProvider
                            case self.db.table_user.uri:
                                self.db.table_user.insert(data=content_values)
                                # No action needed

                            # MasterSlave Content Provider
                            case self.db.table_master_slave.uri:
                                self.db.table_master_slave.insert(data=content_values)
                                # No action needed

                            # Automation Content Provider
                            case self.db.table_automation.uri:
                                self.db.table_automation.insert(content_values)
                                # No action needed

                            # Sensor Content Provider
                            case self.db.table_sensor.uri:
                                self.db.table_sensor.insert(data=content_values)
                                self._state.sync_zones_data(self.get_zones_from_db())

                            # Door Lock Content Provider
                            case self.db.table_doorlock.uri:
                                self.db.table_doorlock.insert(data=content_values)
                                self._state.sync_zwave_devices_data(self.get_zwave_devices_from_db())

                            # Dimmer Content Provider
                            case self.db.table_dimmer.uri:
                                self.db.table_dimmer.insert(data=content_values)
                                self._state.sync_zwave_devices_data(self.get_zwave_devices_from_db())

                            # Thermostat Content Provider
                            case self.db.table_thermostat.uri:
                                self.db.table_thermostat.insert(data=content_values)
                                self._state.sync_zwave_devices_data(self.get_zwave_devices_from_db())

                            #ZWave Node Content Provider
                            case self.db.table_zwave_node.uri:
                                self.db.table_zwave_node.insert(data=content_values)
                                self._state.sync_zwave_devices_data(self.get_zwave_devices_from_db())

                            # HistoryContentProvider
                            case self.db.table_history.uri:
                                self.db.table_history.insert(data=content_values)
                                # No action needed

                            # AlarmedSensorProvider
                            case self.db.table_alarmedsensor.uri:

                                partition_id = content_values.get("partition_id","")
                                self.db.table_alarmedsensor.insert(data=content_values)

                                partition = self._state.partition(partition_id)
                                if partition is not None:
                                    partition.append_alarm_type([PartitionAlarmType(content_values.get("sgroup",""))])

                            # IQRemoteSettingsProvider
                            case self.db.table_iqremotesettings.uri:
                                self.db.table_iqremotesettings.insert(data=content_values)
                                # No action needed

                            # HeatMapContentProvider
                            case self.db.table_heat_map.uri:
                                self.db.table_heat_map.insert(data=content_values)
                                # No action needed

                            # ZDeviceHistoryContentProvider
                            case self.db.table_zwave_history.uri:
                                self.db.table_zwave_history.insert(data=content_values)
                                # No action needed

                            # Dashboard Message Content Provider
                            case self.db.table_dashboard_msgs.uri:
                                self.db.table_dashboard_msgs.insert(data=content_values)
                                # No action needed


                            case _:
                                LOGGER.debug("iq2meid inserting unknow uri:%s",uri)
                                LOGGER.debug(data)

                    case _:
                        LOGGER.debug("iq2meid - Unknow dboperation: %s",dbOperation)
                        LOGGER.debug(data)
            case _:
                LOGGER.debug("iq2meid - Unknow event: %s",eventName)
                LOGGER.debug(data)

    def check_user(self,user_code:str) -> int:
        for user in self._users:
            if user["user_code"] == user_code:
                return user["id"]

        # No valid user code found
        return -1

    def get_zwave_devices_from_db(self) -> list[QolsysZWaveDevice]:
        devices = []
        devices_list = self.db.get_zwave_devices()
        dimmers_list = self.db.get_dimmers()
        thermostats_list = self.db.get_thermostats()
        locks_list = self.db.get_locks()

        for device in devices_list:

            device_added = False

            zwave_node_id = device.get("node_id","")
            # Check if z-wave device is a Dimmer
            for d in dimmers_list:
                dimmer_node_id = d.get("node_id","")

                # Found a Dimmer
                if zwave_node_id == dimmer_node_id:
                    qolsys_dimmer = QolsysDimmer(d,device)
                    devices.append(qolsys_dimmer)
                    device_added = True
                    break

            # Check is z-wave devie is a Thermostat
            for thermostat in thermostats_list:
                thermostat_node_id = thermostat.get("node_id","")

                # Found a Thermostat
                if zwave_node_id == thermostat_node_id:
                    qolsys_thermostat = QolsysThermostat(thermostat,device)
                    devices.append(qolsys_thermostat)
                    device_added = True
                    break

            # Check is z-wave device is a Lock
            for lock in locks_list:
                lock_node_id = lock.get("node_id","")

                # Found a Lock
                if zwave_node_id == lock_node_id:
                    qolsys_lock = QolsysLock(lock,device)
                    devices.append(qolsys_lock)
                    device_added = True
                    break

            # Found a SmartOutlet

            # Found Garage Door Openner

            # No Specific z-wave device found, add a generic z-wave device
            if not device_added:
                qolsys_generic = QolsysGeneric()
                devices.append(qolsys_generic)

        return devices

    def get_zones_from_db(self) -> list[QolsysZone]:
        zones = []
        zones_list:list[dict] = self.db.get_zones()

         # Create sensors array
        for zone_info in zones_list:
            zones.append(QolsysZone(zone_info))

        return zones

    def get_partitions_from_db(self) -> list[QolsysPartition]:

        partitions = []
        partition_list:list[dict] = self.db.get_partitions()

        # Create partitions array
        for partition_dict in partition_list:

            partition_id = partition_dict["partition_id"]

            settings_dict = {
                "SYSTEM_STATUS": self.db.get_setting_partition("SYSTEM_STATUS",partition_id) or "UNKNOWN",
                "SYSTEM_STATUS_CHANGED_TIME": self.db.get_setting_partition("SYSTEM_STATUS_CHANGED_TIME",partition_id) or "",
                "EXIT_SOUNDS": self.db.get_setting_partition("EXIT_SOUNDS",partition_id) or "",
                "ENTRY_DELAYS":  self.db.get_setting_partition("ENTRY_DELAYS",partition_id) or "",
            }

            alarm_type = []
            for alarm in self.db.get_alarm_type(partition_id):
                if alarm == "":
                    alarm_type.append(PartitionAlarmType("Police Emergency"))
                else:
                    alarm_type.append(PartitionAlarmType(alarm))

            alarm_state = PartitionAlarmState(self.db.get_state_partition("ALARM_STATE",partition_id) or "UNKNOWN")

            partition = QolsysPartition(partition_dict,settings_dict,alarm_state,alarm_type)
            partitions.append(partition)

        return partitions

    def dump(self) -> None:
        LOGGER.debug("*** Qolsys Panel Information ***")
        LOGGER.debug("Android Version: %s",self.ANDROID_VERSION)
        LOGGER.debug("Hardware Version: %s",self.HARDWARE_VERSION)
        LOGGER.debug("MAC Address: %s",self.MAC_ADDRESS)
        LOGGER.debug("Unique ID: %s",self.unique_id)
        LOGGER.debug("Panel Tamper State: %s",self.PANEL_TAMPER_STATE)
        LOGGER.debug("AC Status: %s",self.AC_STATUS)
        LOGGER.debug("Battery Status: %s",self.BATTERY_STATUS)
        LOGGER.debug("GSM Connection Status: %s",self.GSM_CONNECTION_STATUS)
        LOGGER.debug("GSM Signal Strength: %s",self.GSM_SIGNAL_STRENGTH)
        LOGGER.debug("Fail To Communicate: %s",self.FAIL_TO_COMMUNICATE)
        LOGGER.debug("System Time: %s",datetime.fromtimestamp(int(self.SYSTEM_TIME)/1000))
        LOGGER.debug("Country: %s",self.COUNTRY)
        LOGGER.debug("Language: %s",self.LANGUAGE)
        LOGGER.debug("Temp Format: %s",self.TEMPFORMAT)
        LOGGER.debug("Z-Wave Firmware Version: %s",self.ZWAVE_FIRM_WARE_VERSION)
        LOGGER.debug("Z-Wave Card Present: %s",self.ZWAVE_CARD)
        LOGGER.debug("Z-Wave Controller Enabled: %s",self.ZWAVE_CONTROLLER)
        LOGGER.debug("Partitons Enabled: %s",self.PARTITIONS)
        LOGGER.debug("Control4 Enabled: %s",self.CONTROL_4)
        LOGGER.debug("Six Digit User Code Enabled: %s",self.SIX_DIGIT_USER_CODE)
        LOGGER.debug("Secure Arming: %s",self.SECURE_ARMING)
        LOGGER.debug("Auto-Stay: %s",self.AUTO_STAY)
        LOGGER.debug("Auto-Bypass: %s",self.AUTO_BYPASS)
        LOGGER.debug("Auto-Arm-Stay: %s",self.AUTO_ARM_STAY)
        LOGGER.debug("Auto-Exit-Extension: %s",self.AUTO_EXIT_EXTENSION)
        LOGGER.debug("Final-Exit-Door-Arming: %s",self.FINAL_EXIT_DOOR_ARMING)
        LOGGER.debug("No-Arm-Low-Battery: %s",self.NO_ARM_LOW_BATTERY)
        LOGGER.debug("Normal Entry Delay: %s",self.TIMER_NORMAL_ENTRY_DELAY)
        LOGGER.debug("Normal Exit Delay: %s",self.TIMER_NORMAL_EXIT_DELAY)
        LOGGER.debug("Long Entry Delay: %s",self.TIMER_LONG_ENTRY_DELAY)
        LOGGER.debug("Long Exit Delay: %s",self.TIMER_LONG_EXIT_DELAY)
        LOGGER.debug("Auxiliary Panic Enabled: %s",self.AUXILIARY_PANIC_ENABLED)
        LOGGER.debug("Fire Panic Enabled: %s",self.FIRE_PANIC_ENABLED)
        LOGGER.debug("Police Panic Enabled: %s",self.POLICE_PANIC_ENABLED)
        LOGGER.debug("Night Mode Settings: %s",self.NIGHTMODE_SETTINGS)
        LOGGER.debug("Night Mode Settings Stage: %s",self.NIGHT_SETTINGS_STATE)
        LOGGER.debug("Show Security Sensors: %s",self.SHOW_SECURITY_SENSORS)

        LOGGER.debug("Users list:")
        for user in self._users:
            LOGGER.debug("User: %s",user["id"])

