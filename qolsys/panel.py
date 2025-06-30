import json
import logging

from qolsys.partition import QolsysPartition
from qolsys.sensor import QolsysSensor
from qolsys.zwave_device import QolsysZWaveDevice
from qolsys.utils_mqtt import mqtt_arming_status_to_C4

LOGGER = logging.getLogger(__name__)

class QolsysPanel():
    def __init__(self,settings_directory:str):

        self._users = []
        self._settings_directory = settings_directory

        self._database = None
        self._HistoryContentProvider = "content://com.qolsys.qolsysprovider.HistoryContentProvider/history"
        self._SettingsProvider = "content://com.qolsys.qolsysprovider.QolsysSettingsProvider/qolsyssettings"
        self._PartitionContentProvider = "content://com.qolsys.qolsysprovider.PartitionContentProvider/partition"
        self._SensorContentProvider = "content://com.qolsys.qolsysprovider.SensorContentProvider/sensor"
        self._ZwaveContentProvider = "content://com.qolsys.qolsysprovider.ZwaveContentProvider/zwave_node"
        self._DimmerLightsContentProvider = "content://com.qolsys.qolsysprovider.DimmerLightsContentProvider/dimmerlight"
        self._ZwaveContentProvider = "content://com.qolsys.qolsysprovider.ZwaveContentProvider/zwave_node"
        self._ZwaveContentProvider = "content://com.qolsys.qolsysprovider.ZwaveContentProvider/zwave_node"
        self._StateContentProvider = "content://com.qolsys.qolsysprovider.StateContentProvider/state"
        self._ThermostatsContentProvider = "content://com.qolsys.qolsysprovider.ThermostatsContentProvider/thermostat"
        self._EUEventContentProvider = "content://com.qolsys.qolsysprovider.EUEventContentProvider/eu_event"
        self._TccContentProvider = "content://com.qolsys.qolsysprovider.TccContentProvider/tcc"
        self._UserContentProvider = "content://com.qolsys.qolsysprovider.UserContentProvider/user"
        self._AlarmedSensorProvider = "content://com.qolsys.qolsysprovider.AlarmedSensorProvider/alarmedsensor"
        self._TroubleConditionsContentProvider = "content://com.qolsys.qolsysprovider.TroubleConditionsContentProvider/trouble_conditions"
        self._HeatMapContentProvider = "content://com.qolsys.qolsysprovider.HeatMapContentProvider/heat_map"
        self._MasterSlaveContentProvider = "content://com.qolsys.qolsysprovider.MasterSlaveContentProvider/master_slave"
        self._DashboardMessagesContentProvider = "content://com.qolsys.qolsysprovider.DashboardMessagesContentProvider/dashboard_msgs"
        self._VirtualDeviceContentProvider = "content://com.qolsys.qolsysprovider.VirtualDeviceContentProvider/virtual_device"
        self._IQRemoteSettingsContentProvider = "IQRemoteSettingsContentProvider/iqremotesettings"

        # Loading user_code dataf from users.conf file
        try:
            with open(self._settings_directory + 'users.conf') as fd:
                try:
                    users = json.load(fd)
                    for user in users:
                        self._users.append(user)

                except json.JSONDecodeError as e:
                    LOGGER.error(f'users.conf file json error: {e}"')
                    return
                    
        except FileNotFoundError:
            LOGGER.error(f'users.conf file not found')
            return

    def load_database(self,database:dict):
        if not database:
            LOGGER.error(f'Loading Database Error, No Data Provided')

        self._database = database

    def check_user(self,user_code:str) -> int:
        for user in self._users:
            if user['user_code'] == user_code:
                return user['id']

        # No valid user code found
        return -1

    def get_partitions(self):

        partitions = []

        partition_list = []
        sensor_list = []
        zwave_list = []

        # Get partitions list
        for uri in self._database:
            if(uri.get('uri') == self._PartitionContentProvider):
                partition_list = uri.get('resultSet')
                break

         # Get sensors list
        for uri in self._database:
            if uri.get('uri') == self._SensorContentProvider:
                sensor_list = uri.get('resultSet')
                break

          # Get zwave
        for uri in self._database:
            if(uri.get('uri') == self._ZwaveContentProvider):
                zwave_list = uri.get('resultSet')

        # Create partitions array
        partition_list = sorted(partition_list, key=lambda d: d['partition_id'])
        for partition_info in partition_list:
            
            partition_id = int(partition_info['partition_id'])
            partition_name = partition_info['name']
            partition_status = self.get_partition_status(partition_id)
            partition_secure_arm = self.get_secure_arming()

            partition = QolsysPartition(partition_id,
                                        partition_name,
                                        partition_status,
                                        partition_secure_arm)
            partitions.append(partition)

        # Create sensors array
        sensor_list = sorted(sensor_list, key=lambda d: d['zoneid'])
        for sensor_info in sensor_list:

            sensor_status = 'Closed'
            if sensor_info['sensorstatus'] == 'Active':
                sensor_status = 'Open'
            
            sensor = QolsysSensor(int(sensor_info['_id']),
                                  sensor_info['sensorname'],
                                  sensor_info['sensorgroup'],
                                  sensor_status,
                                  sensor_info['sensorstate'],
                                  int(sensor_info['zoneid']),
                                  int(sensor_info['zone_type']),
                                  int(sensor_info['zone_physical_type']),
                                  int(sensor_info['zone_alarm_type']),
                                  int(sensor_info['partition_id']))
            
            # Add sensor to respective partition       
            for partition in partitions:
                if int(partition._id) == int(sensor._partition_id):
                    partition.add_sensor(sensor)

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

            for partition in partitions:
                if int(partition._id) == device._partition_id:
                    partition.add_zwave_device(device)

        return partitions
    
    def get_secure_arming(self):
                 
        for uri in self._database:
            if(uri.get('uri') == self._SettingsProvider):
                settings_list = uri.get('resultSet')

                for setting in settings_list:
                    if setting['name'] == 'SECURE_ARMING':
                        if setting['value'] not in ['true','false']:
                            LOGGER.error(f'Unknow secure_arming value: {setting['value']}')

                        if setting['value'] == 'true':
                            return True
                        
                        if setting['value'] == 'false':
                            return False

        # Not Value found
        LOGGER.error(f'secure_arming value not found')

    def get_partition_status(self,partition_id:int)->str:
        
        history_list = []

        # Get history
        for uri in self._database:
            if(uri.get('uri') == self._HistoryContentProvider):
                history_list = uri.get('resultSet')

        # Get last partition status from history
        status = ["Arm-Away","Arm-Stay","Disarmed","Triggered Alarm"]

        for item in history_list:
            events = item['events']
            item_partition_id =  int(item['partition_id'])
                                    
            if events in status and partition_id == item_partition_id :
               partition_status = mqtt_arming_status_to_C4(events) 
               return partition_status
                
    def dump(self):
        LOGGER.debug(f'*** Qolsys Panel Information ***')
        LOGGER.debug(f'Secure Arming: {self.get_secure_arming()}')

        LOGGER.debug(f'Users list:')
        for user in self._users:
            LOGGER.debug(f'User {user['id']}')
            

