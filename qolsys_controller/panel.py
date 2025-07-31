import asyncio
import json
import logging
from datetime import datetime

from qolsys_controller.partition import QolsysPartition
from qolsys_controller.zone import QolsysSensor
from qolsys_controller.state import QolsysState
from qolsys_controller.observable import QolsysObservable
from qolsys_controller.zone import QolsysSensor
from qolsys_controller.zwave_device import QolsysZWaveDevice
from qolsys_controller.db import QolsysDB
from qolsys_controller.zwave_dimmer import QolsysDimmer
from qolsys_controller.zwave_generic import QolsysGeneric

LOGGER = logging.getLogger(__name__)

class QolsysPanel(QolsysObservable):
    def __init__(self,settings_directory:str,state:QolsysState):

        self._state = state
        self._db = QolsysDB()

        # Partition settings
        self.settings_partition = ['SYSTEM_STATUS','EXIT_SOUNDS','ENTRY_DELAYS','SYSTEM_STATUS_CHANGED_TIME']
        self.state_partition = ['ALARM_STATE']
        
        # Panel settings
        self.settings_panel_observer = QolsysObservable()
        self.settings_panel = ['PANEL_TAMPER_STATE','AC_STATUS','BATTERY_STATUS','FAIL_TO_COMMUNICATE','SECURE_ARMING',
                                'AUTO_BYPASS','AUTO_STAY','AUTO_ARM_STAY','AUTO_EXIT_EXTENSION','FINAL_EXIT_DOOR_ARMING'
                                'NO_ARM_LOW_BATTERY','TEMPFORMAT','LANGUAGE','COUNTRY','SYSTEM_TIME','GSM_CONNECTION_STATUS',
                                'GSM_SIGNAL_STRENGTH','ANDROID_VERSION','HARDWARE_VERSION','TIMER_NORMAL_ENTRY_DELAY',
                                'TIMER_NORMAL_EXIT_DELAY','TIMER_LONG_ENTRY_DELAY','TIMER_LONG_EXIT_DELAY','ZWAVE_CONTROLLER',
                                'ZWAVE_CARD','POLICE_PANIC_ENABLED','FIRE_PANIC_ENABLED','AUXILIARY_PANIC_ENABLED','NIGHTMODE_SETTINGS',
                                'NIGHT_SETTINGS_STATE','PARTITIONS','SIX_DIGIT_USER_CODE','SHOW_SECURITY_SENSORS','SYSTEM_LOGGED_IN_USER',
                                'PANEL_SCENES_SETTING','CONTROL_4','ZWAVE_FIRM_WARE_VERSION','FINAL_EXIT_DOOR_ARMING','NO_ARM_LOW_BATTERY','MAC_ADDRESS' ]

        self._PANEL_TAMPER_STATE = ''
        self._AC_STATUS = ''
        self._BATTERY_STATUS = ''
        self._FAIL_TO_COMMUNICATE = ''
        self._SECURE_ARMING = ''
        self._AUTO_BYPASS = ''
        self._AUTO_STAY = ''
        self._AUTO_ARM_STAY = ''
        self._AUTO_EXIT_EXTENSION = ''
        self._FINAL_EXIT_DOOR_ARMING = ''
        self._NO_ARM_LOW_BATTERY = ''
        self._TEMPFORMAT = ''
        self._LANGUAGE = ''
        self._COUNTRY = ''
        self._SYSTEM_TIME = ''
        self._GSM_CONNECTION_STATUS = ''
        self._GSM_SIGNAL_STRENGTH = ''
        self._ANDROID_VERSION = ''
        self._HARDWARE_VERSION = ''
        self._TIMER_NORMAL_ENTRY_DELAY = ''
        self._TIMER_NORMAL_EXIT_DELAY = ''
        self._TIMER_LONG_ENTRY_DELAY = ''
        self._TIMER_LONG_EXIT_DELAY = ''
        self._ZWAVE_FIRM_WARE_VERSION = ''
        self._ZWAVE_CONTROLLER = ''
        self._ZWAVE_CARD = ''
        self._POLICE_PANIC_ENABLED = ''
        self._FIRE_PANIC_ENABLED = ''
        self._AUXILIARY_PANIC_ENABfLED = ''
        self._NIGHTMODE_SETTINGS = ''
        self._NIGHT_SETTINGS_STATE = ''
        self._PARTITIONS = ''
        self._SIX_DIGIT_USER_CODE = ''
        self._SHOW_SECURITY_SENSORS = ''
        self._CONTROL_4 = ''
        self._MAC_ADDRESS = ''
        self._SYSTEM_LOGGED_IN_USER = ''
        self._PANEL_SCENES_SETTING = ''
        
        self._users = []
        self._unique_id = ''
        self._settings_directory = settings_directory

        self._imei = ''
        self._product_type = ''

    def read_users_file(self) -> bool:
        # Loading user_code data from users.conf file
        try:
            with open(self._settings_directory + 'users.conf') as fd:
                try:
                    users = json.load(fd)
                    for user in users:
                        self._users.append(user)

                except json.JSONDecodeError as e:
                    LOGGER.error(f'users.conf file json error: {e}"')
                    return False
                    
        except FileNotFoundError:
            LOGGER.error(f'users.conf file not found')
            return False
        
        return True
        
    @property
    def db(self):
        return self._db

    @property
    def ANDROID_VERSION(self):
        self._ANDROID_VERSION = self.db.get_setting_panel('ANDROID_VERSION')
        return self._ANDROID_VERSION
    
    @property
    def PANEL_TAMPER_STATE(self):
        self._PANEL_TAMPER_STATE = self.db.get_setting_panel('PANEL_TAMPER_STATE')
        return self._PANEL_TAMPER_STATE
    
    @property
    def AC_STATUS(self):
        self._AC_STATUS = self.db.get_setting_panel('AC_STATUS')
        return self._AC_STATUS
    
    @property
    def BATTERY_STATUS(self):
        self._BATTERY_STATUS = self.db.get_setting_panel('BATTERY_STATUS')
        return self._BATTERY_STATUS

    @property
    def FAIL_TO_COMMUNICATE(self):
        self._FAIL_TO_COMMUNICATE = self.db.get_setting_panel('FAIL_TO_COMMUNICATE')
        return self._FAIL_TO_COMMUNICATE
    
    @property
    def SECURE_ARMING(self):
        self._SECURE_ARMING = self.db.get_setting_panel('SECURE_ARMING')
        return self._SECURE_ARMING
    
    @property
    def AUTO_BYPASS(self):
        self._AUTO_BYPASS = self.db.get_setting_panel('AUTO_BYPASS')
        return self._AUTO_BYPASS
    
    @property
    def AUTO_STAY(self):
        self._AUTO_STAY = self.db.get_setting_panel('AUTO_STAY')
        return self._AUTO_STAY

    @property
    def AUTO_ARM_STAY(self):
        self._AUTO_ARM_STAY = self.db.get_setting_panel('AUTO_ARM_STAY')
        return self._AUTO_ARM_STAY
    
    @property
    def AUTO_EXIT_EXTENSION(self):
        self._AUTO_EXIT_EXTENSION = self.db.get_setting_panel('AUTO_EXIT_EXTENSION')
        return self._AUTO_EXIT_EXTENSION
    
    @property
    def FINAL_EXIT_DOOR_ARMING(self):
        self._FINAL_EXIT_DOOR_ARMING = self.db.get_setting_panel('FINAL_EXIT_DOOR_ARMING')
        return self._FINAL_EXIT_DOOR_ARMING
    
    @property
    def NO_ARM_LOW_BATTERY(self):
        self._NO_ARM_LOW_BATTERY = self.db.get_setting_panel('NO_ARM_LOW_BATTERY')
        return self._NO_ARM_LOW_BATTERY
    
    @property
    def TEMPFORMAT(self):
        self._TEMPFORMAT = self.db.get_setting_panel('TEMPFORMAT')
        return self._TEMPFORMAT
    
    @property
    def LANGUAGE(self):
        self._LANGUAGE = self.db.get_setting_panel('LANGUAGE')
        return self._LANGUAGE

    @property
    def COUNTRY(self):
        self._COUNTRY = self.db.get_setting_panel('COUNTRY')
        return self._COUNTRY
    
    @property
    def SYSTEM_TIME(self):
        self._SYSTEM_TIME = self.db.get_setting_panel('SYSTEM_TIME')
        return self._SYSTEM_TIME
    
    @property
    def GSM_CONNECTION_STATUS(self):
        self._GSM_CONNECTION_STATUS = self.db.get_setting_panel('GSM_CONNECTION_STATUS')
        return self._GSM_CONNECTION_STATUS
    
    @property
    def GSM_SIGNAL_STRENGTH(self):
        self._GSM_SIGNAL_STRENGTH = self.db.get_setting_panel('GSM_SIGNAL_STRENGTH')
        return self._GSM_SIGNAL_STRENGTH
    
    @property
    def HARDWARE_VERSION(self):
        self._HARDWARE_VERSION = self.db.get_setting_panel('HARDWARE_VERSION')
        return self._HARDWARE_VERSION
    
    @property
    def ZWAVE_FIRM_WARE_VERSION(self):
        self._ZWAVE_FIRM_WARE_VERSION = self.db.get_setting_panel('ZWAVE_FIRM_WARE_VERSION')
        return self._ZWAVE_FIRM_WARE_VERSION
    
    @property
    def ZWAVE_CONTROLLER(self):
        self._ZWAVE_CONTROLLER = self.db.get_setting_panel('ZWAVE_CONTROLLER')
        return self._ZWAVE_CONTROLLER
    
    @property
    def ZWAVE_CARD(self):
        self._ZWAVE_CARD = self.db.get_setting_panel('ZWAVE_CARD')
        return self._ZWAVE_CARD

    @property
    def POLICE_PANIC_ENABLED(self):
        self._POLICE_PANIC_ENABLED = self.db.get_setting_panel('POLICE_PANIC_ENABLED')
        return self._POLICE_PANIC_ENABLED
    
    @property
    def FIRE_PANIC_ENABLED(self):
        self._FIRE_PANIC_ENABLED = self.db.get_setting_panel('FIRE_PANIC_ENABLED')
        return self._FIRE_PANIC_ENABLED
    
    @property
    def AUXILIARY_PANIC_ENABLED(self):
        self._AUXILIARY_PANIC_ENABLED = self.db.get_setting_panel('AUXILIARY_PANIC_ENABLED')
        return self._AUXILIARY_PANIC_ENABLED
    
    @property
    def PARTITIONS(self):
        self._PARTITIONS = self.db.get_setting_panel('PARTITIONS')
        return self._PARTITIONS
    
    @property
    def SIX_DIGIT_USER_CODE(self):
        self._SIX_DIGIT_USER_CODE = self.db.get_setting_panel('SIX_DIGIT_USER_CODE')
        return self._SIX_DIGIT_USER_CODE
    
    @property
    def CONTROL_4(self):
        self._CONTROL_4 = self.db.get_setting_panel('CONTROL_4')
        return self._CONTROL_4
    
    @property
    def NIGHTMODE_SETTINGS(self):
        self._NIGHTMODE_SETTINGS = self.db.get_setting_panel('NIGHTMODE_SETTINGS')
        return self._NIGHTMODE_SETTINGS
    
    @property
    def NIGHT_SETTINGS_STATE(self):
        self._NIGHT_SETTINGS_STATE = self.db.get_setting_panel('NIGHT_SETTINGS_STATE')
        return self._NIGHT_SETTINGS_STATE
    
    @property
    def SHOW_SECURITY_SENSORS(self):
        self._SHOW_SECURITY_SENSORS = self.db.get_setting_panel('SHOW_SECURITY_SENSORS')
        return self._SHOW_SECURITY_SENSORS
    
    @property
    def TIMER_NORMAL_ENTRY_DELAY(self):
        self._TIMER_NORMAL_ENTRY_DELAY = self.db.get_setting_panel('TIMER_NORMAL_ENTRY_DELAY')
        return self._TIMER_NORMAL_ENTRY_DELAY
    
    @property
    def TIMER_NORMAL_EXIT_DELAY(self):
        self._TIMER_NORMAL_EXIT_DELAY = self.db.get_setting_panel('TIMER_NORMAL_EXIT_DELAY')
        return self._TIMER_NORMAL_EXIT_DELAY
    
    @property
    def TIMER_LONG_ENTRY_DELAY(self):
        self._TIMER_LONG_ENTRY_DELAY = self.db.get_setting_panel('TIMER_LONG_ENTRY_DELAY')
        return self._TIMER_LONG_ENTRY_DELAY
    
    @property
    def  MAC_ADDRESS(self):
        self._MAC_ADDRESS = self.db.get_setting_panel('MAC_ADDRESS')
        return self._MAC_ADDRESS
    
    @MAC_ADDRESS.setter
    def MAC_ADDRESS(self, value):
        self._MAC_ADDRESS = value
    
    @property
    def unique_id(self):
        mac_address = self.MAC_ADDRESS
        return mac_address.replace(':','')
    
    @property
    def TIMER_LONG_EXIT_DELAY(self):
        self._TIMER_LONG_EXIT_DELAY = self.db.get_setting_panel('TIMER_LONG_ENTRY_DELAY')
        return self._TIMER_LONG_EXIT_DELAY
    
    @property
    def imei(self):
        return self._imei
    
    @imei.setter
    def imei(self,value):
        self._imei = value

    @property
    def product_type(self):
        return self._product_type
    
    @product_type.setter
    def product_type(self,value):
        self._product_type = value

    @property
    def SYSTEM_LOGGED_IN_USER(self):
        self._SYSTEM_LOGGED_IN_USER = self.db.get_setting_panel('SYSTEM_LOGGED_IN_USER')
        return self._SYSTEM_LOGGED_IN_USER
    
    @SYSTEM_LOGGED_IN_USER.setter
    def SYSTEM_LOGGED_IN_USER(self,value):
        self._SYSTEM_LOGGED_IN_USER = value

    @property
    def PANEL_SCENES_SETTING(self):
        self._PANEL_SCENES_SETTING = self.db.get_setting_panel('PANEL_SCENES_SETTING')
        return self.PANEL_SCENES_SETTING
    
    @PANEL_SCENES_SETTING.setter
    def PANEL_SCENES_SETTING(self,value):
        return self._PANEL_SCENES_SETTING

    def load_database(self,database:dict):
        self.db.load_db(database)
        partitions = self.get_partitions()
        zones = self.get_zones()
        zwave_devices = self.get_zwave_devices()
        self._state.load_data(partitions,zones,zwave_devices)

    # Parse panel update to database
    def parse_iq2meid_message(self,data:dict) -> bool:

        eventName = data.get('eventName')
        dbOperation = data.get('dbOperation')
        uri = data.get('uri')

        match eventName:
            
            case 'dbChanged':
  
                match dbOperation:

                    case 'update':
                        content_values = data.get('contentValues')
                        selection = data.get('selection')
                        selection_argument = data.get('selectionArgs')

                        match uri:

                            # Update Settings
                            case self.db.URI_SettingsProvider:
                                name = content_values.get('name','')
                                new_value = content_values.get('value','')
                                old_value = self.db.get_setting_panel(name)
                                self.db.update_table(self.db.Table_QolsysSettingsProvider,selection,selection_argument,content_values)

                                # Update Panel Settings - Send notification if settings ha changed
                                if name in self.settings_panel:
                                    if old_value != new_value:
                                        self.settings_panel_observer.notify()
                                        
                                # Update Partition setting - Send notification if setting has changed
                                if name in self.settings_partition:
                                    partition_id = content_values.get('partition_id','')
                                    partition = self._state.partition(int(partition_id))
                                    if partition != None:
                                        match name:
                                            case 'SYSTEM_STATUS': partition.system_status = new_value
                                            case 'SYSTEM_STATUS_CHANGED_TIME': partition.system_status_changed_time = new_value
                                            case 'EXIT_SOUNDS': partition.exit_sounds = new_value
                                            case 'ENTRY_DELAYS': partition.entry_delays = new_value
                                        
                            # Update Sensor
                            case self.db.URI_SensorContentProvider:
                                self.db.update_table(self.db.Table_SensorContentProvider,selection,selection_argument,content_values)
                                zoneid =  content_values.get('zoneid','')
                                zone = self._state.zone(int(zoneid))
                                if zone != None:
                                    zone.update(content_values)

                            # Update State
                            case self.db.URI_StateContentProvider:
                                name = content_values.get('name','')
                                new_value = content_values.get('value','')
                                partition_id = content_values.get('partition_id','')
                                self.db.update_table(self.db.Table_StateContentProvider,selection,selection_argument,content_values)

                                if name in self.state_partition:
                                    partition = self._state.partition(int(partition_id))
                                    if partition != None:
                                        match name:
                                            case 'ALARM_STATE': partition.alarm_state = new_value

                            # Update heat_map
                            case self.db.URI_HeatMapContentProvider:
                                self.db.update_table(self.db.Table_HeatMapContentProvider,selection,selection_argument,content_values)

                            # Update master_slave
                            case self.db.URI_MasterSlaveContentProvider:
                                self.db.update_table(self.db.Table_MasterSlaveContentProvider,selection,selection_argument,content_values)

                            # Update dashboard_msgs
                            case self.db.URI_DashboardMessagesContentProvider:
                                self.db.update_table(self.db.Table_DashboardMessagesContentProvider,selection,selection_argument,content_values)

                            # Update PartitionContentProvider
                            case self.db.URI_PartitionContentProvider:
                                self.db.update_table(self.db.Table_PartitionContentProvider,selection,selection_argument,content_values)
                                print(f'iq2meid: partition{ selection_argument} updated')
                                # Update Partition Status

                            # Update HistoryContentProvider
                            case self.db.URI_HistoryContentProvider:
                                self.db.update_table(self.db.Table_HistoryContentProvider,selection,selection_argument,content_values)

                            # Update DimmerLightsContentProvider
                            case self.db.URI_DimmerLightsContentProvider:
                                self.db.update_table(self.db.Table_DimmerLightsContentProvider,selection,selection_argument,content_values)
                                node_id =  content_values.get('node_id','')
                                node = self._state.zwave_device(int(node_id))
                                if node != None and isinstance(node,QolsysDimmer):
                                    node.update(content_values)

                            # Update ZwaveContentProvider                          
                            case self.db.URI_ZwaveContentProvider:
                                self.db.update_table(self.db.Table_ZwaveContentProvider,selection,selection_argument,content_values)

                            # Update AutomationDeviceContentProvider
                            case self.db.URI_AutomationDeviceContentProvider:
                                self.db.update_table(self.db.Table_AutomationDeviceContentProvider,selection,selection_argument,content_values)

                            case _:
                                print(f'iq2meid updating unknow uri:{uri}')
                                print(data)

                    case 'delete':
                        selection = data.get('selection')
                        selection_argument = data.get('selectionArgs')

                        match uri:

                            case self.db.URI_AlarmedSensorProvider:
                                self.db.delete_table(self.db.Table_AlarmedSensorProvider,selection,selection_argument)

                                # Update partition alarm state
                                # Panel sends selection='partion=' and selection_argument=[0]
                                # For the moment, will resort to updating all panel partition alarm state
                                for partition in self._state.partitions:
                                    alarm_type = self.db.get_alarm_type(str(partition.id))
                                    partition.alarm_type = alarm_type

                            case self.db.URI_HistoryContentProvider:
                                self.db.delete_table(self.db.Table_HistoryContentProvider,selection,selection_argument)

                            case self.db.URI_ZDeviceHistoryContentProvider:
                                self.db.delete_table(self.db.Table_ZDeviceHistoryContentProvider,selection,selection_argument)

                            case _:
                                print(f'iq2meid deleting unknow uri:{uri}')
                                print(data)

                    case 'insert':
                        content_values = data.get('contentValues')
                    
                        match uri:

                            # HistoryContentProvider
                            case self.db.URI_HistoryContentProvider:
                                self.db.add_history(content_values.get('_id'),content_values.get('version',''),content_values.get('opr',''),content_values.get('partition_id',''),content_values.get('device',''),content_values.get('event',''),content_values.get('time',''),content_values.get('ack',''),content_values.get('type',''),content_values.get('feature1',''),content_values.get('device_id',''))

                            # AlarmedSensorProvider
                            case self.db.URI_AlarmedSensorProvider:

                                partition_id = content_values.get('partition_id','')
                                self.db.add_alarmed_sensor(content_values.get('_id',''),
                                                    content_values.get('partition_id',''),
                                                    content_values.get('silenced',''),
                                                    content_values.get('zone_id',''),
                                                    content_values.get('sgroup',''),
                                                    content_values.get('action',''),
                                                    content_values.get('time_out',''),
                                                    content_values.get('type',''),
                                                    content_values.get('priority',''),
                                                    content_values.get('aseb_type',''))

                                
                                partition = self._state.partition(int(partition_id))
                                if partition != None:
                                    partition.append_alarm_type(content_values.get('sgroup',''))

                            # HeatMapContentProvider
                            case self.db.URI_HeatMapContentProvider:
                                self.db.add_heat_map(content_values.get('_id'),content_values.get('version',''),content_values.get('opr',''),content_values.get('partition_id',''),content_values.get('user_id',''),content_values.get('fragment_id',''),content_values.get('element_id',''),content_values.get('count',''),content_values.get('time_stamp',''))
                            
                            # ZDeviceHistoryContentProvider
                            case self.db.URI_ZDeviceHistoryContentProvider:
                                self.db.add_zwave_history(content_values.get('_id'),
                                               content_values.get('version',''),
                                               content_values.get('opr',''),
                                               content_values.get('partition_id',''),
                                               content_values.get('node_id',''),
                                               content_values.get('device_name',''),
                                               content_values.get('source',''),
                                               content_values.get('event',''),
                                               content_values.get('request',''),
                                               content_values.get('response',''),
                                               content_values.get('created_date',''),
                                               content_values.get('updated_date',''),
                                               content_values.get('last_updated_by',''),
                                               content_values.get('field_type',''),
                                               content_values.get('ack',''),
                                               content_values.get('protocol',''))

                            case _:
                                print(f'iq2meid inserting unknow uri:{uri}')
                                print(data)

                    case _:
                        print(f'iq2meid - Unknow dboperation: {dbOperation}') 
                        print(data)               

    def check_user(self,user_code:str) -> int:
        for user in self._users:
            if user['user_code'] == user_code:
                return user['id']

        # No valid user code found
        return -1
    
    def get_zwave_devices(self):
        devices = []
        devices_list = self.db.get_zwave_devices()
        dimmers_list = self.db.get_dimmers()

        for device in devices_list:

            device_added = False

            zwave_node_id = device.get('node_id','')
            # Check if z-wave device is a Dimmer
            for d in dimmers_list:
                dimmer_node_id = d.get('node_id','')
                
                # Found a Dimmer
                if zwave_node_id == dimmer_node_id:
                    qolsys_dimmer = QolsysDimmer(d,device)
                    qolsys_dimmer.base_node_id = zwave_node_id
                    devices.append(qolsys_dimmer)
                    device_added = True
                    break

            # Found a SmartOutlet

            # Found a Thermostat

            # No Specific z-wave device found, add a generic z-wave device
            if not device_added:
                qolsys_generic = QolsysGeneric()
                devices.append(qolsys_generic)

        return devices
    
    def get_zones(self):
        zones = []
        zones_list = self.db.get_zones()
        
         # Create sensors array
        #zones_list = sorted(zones_list, key=lambda d: d['zoneid'])
        for zone_info in zones_list:
            zone = QolsysSensor(int(zone_info['_id']),
                                  zone_info['sensorname'],
                                  zone_info['sensorgroup'],
                                  zone_info['sensorstatus'],
                                  zone_info['sensorstate'],
                                  int(zone_info['zoneid']),
                                  int(zone_info['zone_type']),
                                  int(zone_info['zone_physical_type']),
                                  int(zone_info['zone_alarm_type']),
                                  int(zone_info['partition_id']),
                                  zone_info['battery_status'],
                                  zone_info['sensortype'],
                                  zone_info['latestdBm'],
                                  zone_info['averagedBm'])
            zones.append(zone)

        return zones

    def get_partitions(self):

        partitions = []
        zwave_list = []

        partition_list = self.db.get_partitions()

        # Create partitions array
        for partition_info in partition_list:
            
            partition_id = partition_info['partition_id']
            name = partition_info['name']
            system_status = self.db.get_setting_partition('SYSTEM_STATUS',partition_id)
            system_status_changed_time = self.db.get_setting_partition('SYSTEM_STATUS_CHANGED_TIME',partition_id)
            exit_sounds = self.db.get_setting_partition('EXIT_SOUNDS',partition_id)
            entry_delays = self.db.get_setting_partition('ENTRY_DELAYS',partition_id)
            alarm_type = self.db.get_alarm_type(partition_id)
            alarm_state = self.db.get_state_partition('ALARM_STATE',partition_id)

            partition = QolsysPartition(int(partition_id),
                                        name,
                                        system_status,
                                        system_status_changed_time,
                                        alarm_state,
                                        alarm_type,
                                        entry_delays,
                                        exit_sounds)
            
            partitions.append(partition)
       
        # Create Z-Wave device array
        zwave_list = sorted(zwave_list, key=lambda d: d['node_id'])
        for zwave_info in zwave_list:
            device = QolsysZWaveDevice(int(zwave_info['_id']),
                                       int(zwave_info['node_id']),
                                       zwave_info['node_name'],
                                       zwave_info['node_type'],
                                       zwave_info['node_status'],
                                       int(zwave_info['partition_id']),
                                       zwave_info['node_secure_cmd_cls'],
                                       zwave_info['node_battery_level'],
                                       zwave_info['node_battery_level_value'],
                                       zwave_info['is_node_listening_node'],
                                       zwave_info['basic_report_value'],
                                       zwave_info['switch_multilevel_report_value'],
                                       int(zwave_info['basic_device_type']),
                                       int(zwave_info['generic_device_type']),
                                       int(zwave_info['specific_device_type']),
                                       zwave_info['num_secure_command_class'],
                                       zwave_info['secure_command_class'],
                                       zwave_info['manufacture_id'],
                                       zwave_info['product_type'],
                                       zwave_info['device_protocol'],
                                       zwave_info['paired_status'],
                                       zwave_info['is_device_sleeping'],
                                       zwave_info['is_device_hidden'],
                                       zwave_info['last_updated_date'],
                                       [],
            )

        return partitions

    def dump(self):
        LOGGER.debug(f'*** Qolsys Panel Information ***')
        LOGGER.debug(f'Android Version: {self.ANDROID_VERSION}')
        LOGGER.debug(f'Hardware Version: {self.HARDWARE_VERSION}')
        LOGGER.debug(f'MAC Address: {self.MAC_ADDRESS}')
        LOGGER.debug(f'Unique ID: {self.unique_id}')
        LOGGER.debug(f'Panel Tamper State: {self.PANEL_TAMPER_STATE}')
        LOGGER.debug(f'AC Status: {self.AC_STATUS}')
        LOGGER.debug(f'Battery Status: {self.BATTERY_STATUS}')
        LOGGER.debug(f'GSM Connection Status: {self.GSM_CONNECTION_STATUS}')
        LOGGER.debug(f'GSM Signal Strength: {self.GSM_SIGNAL_STRENGTH}')
        LOGGER.debug(f'Fail To Communicate: {self.FAIL_TO_COMMUNICATE}')
        LOGGER.debug(f'System Time: {datetime.fromtimestamp(int(self.SYSTEM_TIME)/1000)}')
        LOGGER.debug(f'Country: {self.COUNTRY}')
        LOGGER.debug(f'Language: {self.LANGUAGE}')
        LOGGER.debug(f'Temp Format: {self.TEMPFORMAT}')
        LOGGER.debug(f'Z-Wave Firmware Version: {self.ZWAVE_FIRM_WARE_VERSION}')
        LOGGER.debug(f'Z-Wave Card Present: {self.ZWAVE_CARD}')
        LOGGER.debug(f'Z-Wave Controller Enabled: {self.ZWAVE_CONTROLLER}')
        LOGGER.debug(f'Partitons Enabled: {self.PARTITIONS}')
        LOGGER.debug(f'Control4 Enabled: {self.CONTROL_4}')
        LOGGER.debug(f'Six Digit User Code Enabled: {self.SIX_DIGIT_USER_CODE}')
        LOGGER.debug(f'Secure Arming: {self.SECURE_ARMING}')
        LOGGER.debug(f'Auto-Stay: {self.AUTO_STAY}')
        LOGGER.debug(f'Auto-Bypass: {self.AUTO_BYPASS}')
        LOGGER.debug(f'Auto-Arm-Stay: {self.AUTO_ARM_STAY}')
        LOGGER.debug(f'Auto-Exit-Extension: {self.AUTO_EXIT_EXTENSION}')
        LOGGER.debug(f'Final-Exit-Door-Arming: {self.FINAL_EXIT_DOOR_ARMING}')
        LOGGER.debug(f'No-Arm-Low-Battery: {self.NO_ARM_LOW_BATTERY}')
        LOGGER.debug(f'Normal Entry Delay: {self.TIMER_NORMAL_ENTRY_DELAY}')
        LOGGER.debug(f'Normal Exit Delay: {self.TIMER_NORMAL_EXIT_DELAY}')
        LOGGER.debug(f'Long Entry Delay: {self.TIMER_LONG_ENTRY_DELAY}')
        LOGGER.debug(f'Long Exit Delay: {self.TIMER_LONG_EXIT_DELAY}')
        LOGGER.debug(f'Auxiliary Panic Enabled: {self.AUXILIARY_PANIC_ENABLED}')
        LOGGER.debug(f'Fire Panic Enabled: {self.FIRE_PANIC_ENABLED}')
        LOGGER.debug(f'Police Panic Enabled: {self.POLICE_PANIC_ENABLED}')
        LOGGER.debug(f'Night Mode Settings: {self.NIGHTMODE_SETTINGS}')
        LOGGER.debug(f'Night Mode Settings Stage: {self.NIGHT_SETTINGS_STATE}')
        LOGGER.debug(f'Show Security Sensors: {self.SHOW_SECURITY_SENSORS}')

        LOGGER.debug(f'Users list:')
        for user in self._users:
            LOGGER.debug(f'User {user['id']}')
    




            

