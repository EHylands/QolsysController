import logging
import sqlite3
from prettytable import PrettyTable

LOGGER = logging.getLogger(__name__)

class QolsysDB():

    def __init__(self):
        self._db = sqlite3.connect(":memory:")
        self._cursor = self._db.cursor()

        self.Table_QolsysSettingsProvider = 'qolsyssettings'
        self.Table_SensorContentProvider = 'sensor'
        self.Table_StateContentProvider = 'state'
        self.Table_UserContentProvider = 'user'
        self.Table_HeatMapContentProvider = 'heat_map'
        self.Table_AlarmedSensorProvider = 'alarmedsensor'
        self.Table_HistoryContentProvider = 'history'
        self.Table_MasterSlaveContentProvider = 'master_slave'
        self.Table_DashboardMessagesContentProvider = 'dashboard_msgs'
        self.Table_PartitionContentProvider = 'partition'
        self.Table_ThermostatsContentProvider = 'thermostat'
        self.Table_ZwaveContentProvider = 'zwave_node'
        self.Table_DimmerLightsContentProvider = 'dimmerlight'
        self.Table_ZDeviceHistoryContentProvider = 'zwave_history'
        self.Table_AutomationDeviceContentProvider = 'automation'

        self.URI_AutomationDeviceContentProvider = 'content://com.qolsys.qolsysprovider.AutomationDeviceContentProvider/automation'
        self.URI_HistoryContentProvider = "content://com.qolsys.qolsysprovider.HistoryContentProvider/history"
        self.URI_SettingsProvider = "content://com.qolsys.qolsysprovider.QolsysSettingsProvider/qolsyssettings"
        self.URI_PartitionContentProvider = "content://com.qolsys.qolsysprovider.PartitionContentProvider/partition"
        self.URI_SensorContentProvider = "content://com.qolsys.qolsysprovider.SensorContentProvider/sensor"
        self.URI_ZwaveContentProvider = "content://com.qolsys.qolsysprovider.ZwaveContentProvider/zwave_node"
        self.URI_DimmerLightsContentProvider = "content://com.qolsys.qolsysprovider.DimmerLightsContentProvider/dimmerlight"
        self.URI_ZwaveContentProvider = "content://com.qolsys.qolsysprovider.ZwaveContentProvider/zwave_node"
        self.URI_StateContentProvider = "content://com.qolsys.qolsysprovider.StateContentProvider/state"
        self.URI_ThermostatsContentProvider = "content://com.qolsys.qolsysprovider.ThermostatsContentProvider/thermostat"
        self.URI_EUEventContentProvider = "content://com.qolsys.qolsysprovider.EUEventContentProvider/eu_event"
        self.URI_TccContentProvider = "content://com.qolsys.qolsysprovider.TccContentProvider/tcc"
        self.URI_UserContentProvider = "content://com.qolsys.qolsysprovider.UserContentProvider/user"
        self.URI_AlarmedSensorProvider = "content://com.qolsys.qolsysprovider.AlarmedSensorProvider/alarmedsensor"
        self.URI_TroubleConditionsContentProvider = "content://com.qolsys.qolsysprovider.TroubleConditionsContentProvider/trouble_conditions"
        self.URI_HeatMapContentProvider = "content://com.qolsys.qolsysprovider.HeatMapContentProvider/heat_map"
        self.URI_MasterSlaveContentProvider = "content://com.qolsys.qolsysprovider.MasterSlaveContentProvider/master_slave"
        self.URI_DashboardMessagesContentProvider = "content://com.qolsys.qolsysprovider.DashboardMessagesContentProvider/dashboard_msgs"
        self.URI_VirtualDeviceContentProvider = "content://com.qolsys.qolsysprovider.VirtualDeviceContentProvider/virtual_device"
        self.URI_IQRemoteSettingsContentProvider = "IQRemoteSettingsContentProvider/iqremotesettings"
        self.URI_DoorLocksContentProvider = "content://com.qolsys.qolsysprovider.DoorLocksContentProvider/doorlock"
        self.URI_SmartSocketsContentProvider = "content://com.qolsys.qolsysprovider.SmartSocketsContentProvider/smartsocket"
        self.URI_SceneContentProvider = "content://com.qolsys.qolsysprovider.SceneContentProvider/scene"
        self.URI_ZDeviceHistoryContentProvider = "content://com.qolsys.qolsysprovider.ZDeviceHistoryContentProvider/zwave_history"

        self._create_db()

    @property
    def db(self):
        return self._db
    
    @property
    def cursor(self):
        return self._cursor
    
    def delete_table(self,table:str,selection:str,selection_argument:str):
        
        # Selection Argument
        selection_argument = selection_argument.replace('[','')
        selection_argument = selection_argument.replace(']','')
        selection_argument = selection_argument.split(',')

        # Replace '?' in selection string with selectio_argument
        for i in selection_argument:
            selection = selection.replace('?',f'\'{i}\'',1)

        query = f'''DELETE FROM {table} WHERE {selection}'''
        self.cursor.execute(query)
        self.db.commit()

    def update_table(self,table:str,selection:str,selection_argument:str,new_value:str):

        # Panel is sending query parameter for db update in text string
        # Have not found a way to make it work with parametrized query yet
        # Using f string concat for moment ...

        # New Values to update in table
        db_value = []
        for key, value in new_value.items():
            db_value.append(f'{key}=\'{value}\'')
        db_value = ",".join(db_value)

        # Selection Argument
        selection_argument = selection_argument.replace('[','')
        selection_argument = selection_argument.replace(']','')
        selection_argument = selection_argument.split(',')
        
        for i in selection_argument:
            selection = selection.replace('?',f'\'{i}\'',1)

         # Final query
        query = f'''UPDATE {table} SET {db_value} WHERE {selection}'''

        self.cursor.execute(query)
        self.db.commit()

    def get_partitions(self):
        self.cursor.execute(f"SELECT * FROM {self.Table_PartitionContentProvider} ORDER BY partition_id" ) 
        self.db.commit()

        partitions = []
        columns = [description[0] for description in self.cursor.description]
        for row in  self.cursor.fetchall():
            row_dict = dict(zip(columns, row))
            partitions.append(row_dict)
           
        return partitions
    
    def get_zwave_devices(self):
        self.cursor.execute(f"SELECT * FROM {self.Table_ZwaveContentProvider} ORDER BY node_id" ) 
        self.db.commit()

        devices = []
        columns = [description[0] for description in self.cursor.description]
        for row in  self.cursor.fetchall():
            row_dict = dict(zip(columns, row))
            devices.append(row_dict)
           
        return devices

    def get_dimmers(self):
        self.cursor.execute(f"SELECT * FROM {self.Table_DimmerLightsContentProvider} ORDER BY node_id" ) 
        self.db.commit()

        dimmers = []
        columns = [description[0] for description in self.cursor.description]
        for row in  self.cursor.fetchall():
            row_dict = dict(zip(columns, row))
            dimmers.append(row_dict)
           
        return dimmers

    def get_zones(self):
        self.cursor.execute(f"SELECT * FROM {self.Table_SensorContentProvider} ORDER BY zoneid" ) 
        self.db.commit()

        zones = []
        columns = [description[0] for description in self.cursor.description]
        for row in  self.cursor.fetchall():
            row_dict = dict(zip(columns, row))
            zones.append(row_dict)
           
        return zones
    
    def get_setting_panel(self,setting:str):
        self.cursor.execute(f"SELECT value FROM {self.Table_QolsysSettingsProvider} WHERE name = ? and partition_id  = ? ", (setting,'0'))      
        row = self.cursor.fetchone()
        
        if row == None:
            LOGGER.error(f'{setting} value not found')

        return row[0]
    
    def get_setting_partition(self,setting:str,partition_id:str):
        self.cursor.execute(f"SELECT value FROM {self.Table_QolsysSettingsProvider} WHERE name = ? and partition_id  = ? ", (setting,partition_id))      
        row = self.cursor.fetchone()
        
        if row == None:
            LOGGER.error(f'{setting} value not found')

        return row[0]
    
    def get_state_partition(self,state:str,partition_id:str):
        self.cursor.execute(f"SELECT value FROM {self.Table_StateContentProvider} WHERE name = ? and partition_id  = ? ", (state,partition_id))      
        row = self.cursor.fetchone()
        
        if row == None:
            LOGGER.error(f'{state} value not found')

        return row[0]
    
    def get_alarm_type(self,partition_id:str) -> list[str]:
        type = []
        self.cursor.execute(f"SELECT sgroup FROM {self.Table_AlarmedSensorProvider} WHERE partition_id  = ? ", (partition_id)) 
        rows = self.cursor.fetchall()

        for row in rows:
            type.append(row[0])

        return type
     
    def add_partition(self,_id:str,version:str,opr:str,partition_id:str,name:str,devices:str):
        self.cursor.execute(f"INSERT INTO {self.Table_PartitionContentProvider} (_id,version,opr,partition_id,name,devices) VALUES (?,?,?,?,?,?)",(_id,version,opr,partition_id,name,devices))
        self.db.commit()

    def add_setting(self,_id:str,version:str,opr:str,partition_id:str,name:str,value:str):
        self.cursor.execute(f"INSERT INTO {self.Table_QolsysSettingsProvider} (_id,version,opr,partition_id,name,value) VALUES (?,?,?,?,?,?)",(_id,version,opr,partition_id,name,value))
        self.db.commit()

    def add_sensor(self,_id:str,version:str,opr:str,partition_id:str,sensorid:str,sensortype:str,sensorname:str,sensorgroup:str,chimetype:str,sensorstatus:str,time:str,
                      sensorstate:str,sensortts:str,zoneid:str,frame_id:str,zone_alarm_type:str,zone_equipment_code:str,zone_physical_type:str,zone_type:str,zone_rf_sensor:str,
                      zone_supervised:str,zone_two_way_voice_enabled:str,zone_reporting_enabled:str,battery_status:str,created_date:str,created_by:str,updated_date:str,updated_by:str,
                      frame_count:str,frame_type:str,current_capability:str,shortID:str,diag_24hr:str,allowdisarming:str,device_capability:str,sub_type:str,signal_source:str,
                      powerg_manufacture_id:str,parent_node:str,latestdBm:str,averagedBm:str,serial_number:str,extras:str,ac_status:str):
        self.cursor.execute(f"INSERT INTO {self.Table_SensorContentProvider} (_id,version,opr,partition_id,sensorid,sensortype,sensorname,sensorgroup,chimetype,sensorstatus,time,sensorstate,sensortts,zoneid,frame_id,zone_alarm_type,zone_equipment_code,zone_physical_type,zone_type,zone_rf_sensor,zone_supervised,zone_two_way_voice_enabled, zone_reporting_enabled, battery_status,created_date,created_by,updated_date,updated_by,frame_count,frame_type,current_capability,shortID,diag_24hr,allowdisarming,device_capability,sub_type, signal_source, powerg_manufacture_id,parent_node,latestdBm,averagedBm,serial_number,extras,ac_status) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(_id,version,opr,partition_id,sensorid,sensortype,sensorname,sensorgroup,chimetype,sensorstatus,time,sensorstate,sensortts,zoneid,frame_id,zone_alarm_type,zone_equipment_code,zone_physical_type,zone_type,zone_rf_sensor,zone_supervised,zone_two_way_voice_enabled, zone_reporting_enabled, battery_status,created_date,created_by,updated_date,updated_by,frame_count,frame_type,current_capability,shortID,diag_24hr,allowdisarming,device_capability,sub_type, signal_source, powerg_manufacture_id,parent_node,latestdBm,averagedBm,serial_number,extras,ac_status))
        self.db.commit()

    def add_state(self,_id:str,version:str,opr:str,partition_id:str,name:str,value:str,extraparams:str):
        self.cursor.execute(f"INSERT INTO {self.Table_StateContentProvider} (_id,version,opr,partition_id,name,value,extraparams) VALUES (?,?,?,?,?,?,?)",(_id,version,opr,partition_id,name,value,extraparams))
        self.db.commit()

    def add_zwave_node(self,_id:str,version:str,opr:str,partition_id:str,node_id:str,node_name:str,node_type:str,node_status:str,node_secure_cmd_cls:str,
                       node_battery_level:str,node_battery_level_value:str,is_node_listening_node:str,basic_report_value:str,switch_multilevel_report_value:str,
                       basic_device_type:str,generic_device_type:str,specific_device_type:str,num_secure_command_class:str,secure_command_class:str,
                       manufacture_id:str, product_type:str,product_id:str,library_type_version:str,protocol_version:str,protocol_sub_version:str,
                       application_version:str,application_sub_version:str,capability:str,command_class_list:str,lenof_command_class_list:str,security:str,
                       library_type:str,last_updated_date:str,node_battery_level_updated_time:str,basic_report_updated_time:str,switch_multilevel_report_updated_time:str,
                       multi_channel_details:str,rediscover_status:str,last_rediscover_time:str,neighbour_info:str,last_node_test_time:str,
                       endpoint:str,endpoint_details:str,device_wakeup_time:str,role_type:str,is_device_sleeping:str,counters_passed:str,counters_failed:str,group_id:str,
                       command_classes_version:str,paired_status:str,device_dsk:str,endpoint_secure_cmd_cls:str,s2_security_keys:str,device_protocol:str,is_device_hidden:str):
        self.cursor.execute(f'''INSERT INTO {self.Table_ZwaveContentProvider} (_id,version,opr,partition_id,node_id,node_name,node_type,node_status,node_secure_cmd_cls,node_battery_level,
                            node_battery_level_value,is_node_listening_node,basic_report_value,switch_multilevel_report_value,basic_device_type,generic_device_type,
                            specific_device_type,num_secure_command_class,secure_command_class,manufacture_id,product_type,product_id,library_type_version,protocol_version,
                            protocol_sub_version,application_version,application_sub_version,capability,command_class_list,lenof_command_class_list,security,
                            library_type,last_updated_date,node_battery_level_updated_time,basic_report_updated_time,switch_multilevel_report_updated_time,
                            multi_channel_details,rediscover_status,last_rediscover_time,neighbour_info,last_node_test_time,endpoint,endpoint_details,device_wakeup_time,
                            role_type,is_device_sleeping,counters_passed,counters_failed,group_id,command_classes_version,paired_status,device_dsk,endpoint_secure_cmd_cls,
                            s2_security_keys,device_protocol,is_device_hidden) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                            (_id,version,opr,partition_id,node_id,node_name,node_type,node_status,node_secure_cmd_cls,node_battery_level,node_battery_level_value,is_node_listening_node,basic_report_value,switch_multilevel_report_value,
                            basic_device_type,generic_device_type,specific_device_type,num_secure_command_class,secure_command_class,manufacture_id,product_type,product_id,
                            library_type_version,protocol_version,protocol_sub_version,application_version,application_sub_version,capability,command_class_list,lenof_command_class_list,security,
                            library_type,last_updated_date,node_battery_level_updated_time,basic_report_updated_time,switch_multilevel_report_updated_time,multi_channel_details,rediscover_status,last_rediscover_time,
                            neighbour_info,last_node_test_time,endpoint,endpoint_details,device_wakeup_time,role_type,is_device_sleeping,counters_passed,counters_failed,group_id,command_classes_version,paired_status,
                            device_dsk,endpoint_secure_cmd_cls,s2_security_keys,device_protocol,is_device_hidden))                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      
        self.db.commit()

    def add_zwave_history(self,_id:str,version:str,opr:str,partition_id:str,node_id:str,device_name:str,source:str,event:str,request:str,
                          response:str,created_date:str,updated_date:str,last_updated_by:str,field_type:str,ack:str,protocol:str):
        self.cursor.execute(f"INSERT INTO {self.Table_ZDeviceHistoryContentProvider} (_id,version,opr,partition_id,node_id,device_name,source,event,request,response,created_date,updated_date,last_updated_by,field_type,ack,protocol) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(_id,version,opr,partition_id,node_id,device_name,source,event,request,response,created_date,updated_date,last_updated_by,field_type,ack,protocol))                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           
        self.db.commit()  

    def add_automation(self,_id:str,virtual_node_id:str,version:str,opr:str,partition_id:str,end_point:str,extras:str,is_autolocking_enabled:str,
                       device_type:str,endpoint_secure_cmd_classes:str,automation_id:str,device_name:str,protocol:str, node_battery_level_value:str,
                        state:str,last_updated_date:str,manufacturer_id:str,endpoint_cmd_classes:str,device_id:str,nodeid_cmd_classes:str,
                         is_device_hidden:str,nodeid_secure_cmd_classes:str,created_date:str,status:str) : 
        self.cursor.execute(f"INSERT INTO {self.Table_AutomationDeviceContentProvider} (_id,virtual_node_id,version,opr,partition_id,end_point,extras,is_autolocking_enabled,device_type,endpoint_secure_cmd_classes,automation_id,device_name,protocol,node_battery_level_value,state,last_updated_date,manufacturer_id,endpoint_cmd_classes,device_id,nodeid_cmd_classes,is_device_hidden,nodeid_secure_cmd_classes,created_date,status) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(_id,virtual_node_id,version,opr,partition_id,end_point,extras,is_autolocking_enabled,device_type,endpoint_secure_cmd_classes,automation_id,device_name,protocol,node_battery_level_value,state,last_updated_date,manufacturer_id,endpoint_cmd_classes,device_id,nodeid_cmd_classes,is_device_hidden,nodeid_secure_cmd_classes,created_date,status))                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           
        self.db.commit()  

    def add_dimmer_light(self,_id:str,version:str,opr:str,partition_id:str,dimmer_name:str,status:str,node_id:str,level:str,
                         created_by:str,created_date:str,updated_by:str,last_updated_date:str,endpoint:str,power_details:str,paired_status:str):
        self.cursor.execute(f"INSERT INTO {self.Table_DimmerLightsContentProvider} (_id,version,opr,partition_id,dimmer_name,status,node_id,level,created_by,created_date,updated_by,last_updated_date,endpoint,power_details,paired_status) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(_id,version,opr,partition_id,dimmer_name,status,node_id,level,created_by,created_date,updated_by,last_updated_date,endpoint,power_details,paired_status))                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           
        self.db.commit()                     
                       
    def add_thermostat(self,_id:str,version:str,opr:str,partition_id:str,thermostat_id:str,thermostat_name:str,current_temp:str,
                          target_cool_temp:str,target_heat_temp:str,target_temp:str,power_usage:str,thermostat_mode:str,
                          thermostat_mode_bitmask:str,fan_mode:str,fan_mode_bitmask:str,set_point_mode:str,set_point_mode_bitmask:str,
                          node_id:str,created_by:str,created_date:str,updated_by:str,last_updated_date:str,thermostat_mode_updated_time:str,
                          fan_mode_updated_time:str,set_point_mode_updated_time:str,target_cool_temp_updated_time:str,
                          target_heat_temp_updated_time:str,current_temp_updated_time:str,device_temp_unit:str,endpoint:str,paired_status:str,
                          configuration_parameter:str):
        self.cursor.execute(f"INSERT INTO {self.Table_ThermostatsContentProvider} (_id,version,opr,partition_id,thermostat_id,thermostat_name,current_temp,target_cool_temp,target_heat_temp,target_temp,power_usage,thermostat_mode,thermostat_mode_bitmask,fan_mode,fan_mode_bitmask,set_point_mode,set_point_mode_bitmask,node_id,created_by,created_date,updated_by,last_updated_date,thermostat_mode_updated_time,fan_mode_updated_time,set_point_mode_updated_time,target_cool_temp_updated_time,target_heat_temp_updated_time,current_temp_updated_time,device_temp_unit,endpoint,paired_status,configuration_parameter) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(_id,version,opr,partition_id,thermostat_id,thermostat_name,current_temp,target_cool_temp,target_heat_temp,target_temp,power_usage,thermostat_mode,thermostat_mode_bitmask,fan_mode,fan_mode_bitmask,set_point_mode,set_point_mode_bitmask,node_id,created_by,created_date,updated_by,last_updated_date,thermostat_mode_updated_time,fan_mode_updated_time,set_point_mode_updated_time,target_cool_temp_updated_time,target_heat_temp_updated_time,current_temp_updated_time,device_temp_unit,endpoint,paired_status,configuration_parameter))                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           
        self.db.commit()

    def add_user(self,_id:str,version:str,opr:str,partition_id:str,username:str,userPin:str,expirydate:str,usertype:str,userid:str,lastname:str,check_in:str,hash_user:str):
        self.cursor.execute(f"INSERT INTO {self.Table_UserContentProvider} (_id,version,opr,partition_id,username,userPin,expirydate,usertype,userid,lastname,check_in,hash_user) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",(_id,version,opr,partition_id,username,userPin,expirydate,usertype,userid,lastname,check_in,hash_user)) 
        self.db.commit()

    def add_history(self,_id:str,version:str,opr:str,partition_id:str,device:str,events:str,time:str,ack:str,type:str,feature1:str,device_id:str):
        self.cursor.execute(f"INSERT INTO {self.Table_HistoryContentProvider} (_id,version,opr,partition_id,device,events,time,ack,type,feature1,device_id) VALUES (?,?,?,?,?,?,?,?,?,?,?)",(_id,version,opr,partition_id,device,events,time,ack,type,feature1,device_id)) 
        self.db.commit()

    def add_heat_map(self,_id:str,version:str,opr:str,partition_id:str,userid:str,fragment_id:str,element_id:str,count:str,time_stamp:str):
        self.cursor.execute(f"INSERT INTO {self.Table_HeatMapContentProvider} (_id,version,opr,partition_id,userid,fragment_id,element_id,count,time_stamp) VALUES (?,?,?,?,?,?,?,?,?)",(_id,version,opr,partition_id,userid,fragment_id,element_id,count,time_stamp)) 
        self.db.commit()

    def add_alarmed_sensor(self,_id:str,partition_id:str,silenced:str,zone_id:str,sgroup:str,action:str,timed_out:str,type:str,priority:str,aseb_type:str):
        self.cursor.execute(f"INSERT INTO {self.Table_AlarmedSensorProvider} (_id,partition_id,silenced,zone_id,sgroup,action,timed_out,type,priority,aseb_type) VALUES (?,?,?,?,?,?,?,?,?,?)",(_id,partition_id,silenced,zone_id,sgroup,action,timed_out,type,priority,aseb_type)) 
        self.db.commit()

    def add_master_slave(self,_id:str,version:str,opr:str,partition_id:str,zone_id:str,ip_address:str,mac_address:str,device_type:str,
                            created_by:str,created_date:str,updated_by:str,last_updated_date:str,status:str,device_name:str,last_updated_iq_remote_checksum:str,
                            software_version:str,upgrade_status:str,name:str,bssid:str,dhcpInfo:str,topology:str):
        self.cursor.execute(f"INSERT INTO {self.Table_MasterSlaveContentProvider} (_id,version,opr,partition_id,zone_id,ip_address,mac_address,device_type,created_by,created_date,updated_by,last_updated_date,status,device_name,last_updated_iq_remote_checksum,software_version,upgrade_status,name,bssid,dhcpInfo,topology) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(_id,version,opr,partition_id,zone_id,ip_address,mac_address,device_type,created_by,created_date,updated_by,last_updated_date,status,device_name,last_updated_iq_remote_checksum,software_version,upgrade_status,name,bssid,dhcpInfo,topology)) 
        self.db.commit()

    def add_dashboard_msg(self,_id:str,version:str,opr:str,partition_id:str,msg_id:str,title:str,description:str,received_time:str,start_time:str,
                             end_time:str,read:str,mime_type:str):
        self.cursor.execute(f"INSERT INTO {self.Table_DashboardMessagesContentProvider} (_id,version,opr,partition_id,msg_id,title,description,received_time,start_time,end_time,read,mime_type) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",(_id,version,opr,partition_id,msg_id,title,description,received_time,start_time,end_time,read,mime_type)) 
        self.db.commit()
         

    def load_db(self,database:dict):
       
        if not database:
            LOGGER.error(f'Loading Database Error, No Data Provided')

        for uri in database:
            
            match uri.get('uri'):

                # PartitionContentProvider
                case self.URI_PartitionContentProvider:
                    for p in uri.get('resultSet'):
                        self.add_partition(_id = p.get('_id'),
                                              version = p.get('version',''),
                                              opr = p.get('opr',''),
                                              partition_id = p.get('partition_id',''),
                                              name = p.get('name',''),
                                              devices = p.get('devices',''))

                # SensorContentProvider
                case self.URI_SensorContentProvider:
                    for s in uri.get('resultSet'):
                        self.add_sensor(_id = s.get('_id'),
                                            version = s.get('version',''),
                                            opr = s.get('opr',''),
                                            partition_id = s.get('partition_id',''),
                                            sensorid = s.get('sensorid',''),
                                            sensortype = s.get('sensortype',''),
                                            sensorname = s.get('sensorname',''),
                                            ac_status = s.get('ac_status',''),
                                            sensorgroup = s.get('sensorgroup',''),
                                            chimetype = s.get('chimetype',''),
                                            sensorstatus = s.get('sensorstatus',''),
                                            time = s.get('time',''),
                                            sensorstate = s.get('sensorstate',''),
                                            sensortts = s.get('sensortts',''),
                                            zoneid = s.get('zoneid',''),
                                            frame_id = s.get('frame_id',''),
                                            zone_alarm_type = s.get('zone_alarm_type',''),
                                            zone_equipment_code = s.get('zone_equipment_code',''),
                                            zone_physical_type = s.get('zone_physical_type',''),
                                            zone_type = s.get('zone_type',''),
                                            zone_rf_sensor = s.get('zone_rf_sensor',''),
                                            zone_supervised = s.get('zone_supervised',''),
                                            zone_two_way_voice_enabled = s.get('zone_two_way_voice_enabled',''),
                                            zone_reporting_enabled= s.get('zone_reporting_enabled',''),
                                            battery_status = s.get('battery_status',''),
                                            created_date = s.get('created_date',''),
                                            created_by = s.get('created_by',''),
                                            updated_date = s.get('updated_date',''),
                                            updated_by = s.get('updated_by',''),
                                            frame_count = s.get('frame_count',''),
                                            frame_type = s.get('frame_type',''),
                                            current_capability = s.get('current_capability',''),
                                            shortID = s.get('shortID',''),
                                            diag_24hr = s.get('diag_24hr',''),
                                            allowdisarming = s.get('allowdisarming',''),
                                            device_capability = s.get('device_capability',''),
                                            sub_type = s.get('sub_type',''),
                                            signal_source =s.get('signal_source',''),
                                            powerg_manufacture_id = s.get('powerg_manufacture_id',''),
                                            parent_node = s.get('parent_node',''),
                                            latestdBm = s.get('latestdBm',''),
                                            averagedBm = s.get('averagedBm',''),
                                            serial_number = s.get('serial_number',''),
                                            extras= s.get('extras',''))

                # StateContentProvider
                case self.URI_StateContentProvider:
                    for s in uri.get('resultSet'):
                        self.add_state(_id=s.get('_id'),
                                          version = s.get('version',''),
                                          opr = s.get('opr',''),
                                          partition_id = s.get('partition_id',''),
                                          name = s.get('name',''),
                                          value = s.get('value',''),
                                          extraparams = s.get('extraparams',''))
                # AlarmedSensorProvider
                case self.URI_AlarmedSensorProvider:
                    for u in uri.get('resultSet'):
                        self.add_alarmed_sensor(u.get('_id',''),
                                                    u.get('partition_id',''),
                                                    u.get('silenced',''),
                                                    u.get('zonde_id',''),
                                                    u.get('sgroup',''),
                                                    u.get('action',''),
                                                    u.get('time_out',''),
                                                    u.get('type',''),
                                                    u.get('priority',''),
                                                    u.get('aseb_type',''))
                        
                # DashboardMessagesContentProvider
                case self.URI_DashboardMessagesContentProvider:
                    for u in uri.get('resultSet'):
                        self.add_dashboard_msg(u.get('_id'),u.get('version',''),u.get('opr',''),u.get('partition_id',''),u.get('msg_id',''),u.get('title',''),u.get('description',''),u.get('received_time',''),u.get('start_time',''),u.get('end_time',''),u.get('read',''),u.get('mime_type',''))

                # DimmerLightsContentProvider
                case self.URI_DimmerLightsContentProvider:
                    for u in uri.get('resultSet'):
                        self.add_dimmer_light(u.get('_id'),
                                              u.get('version',''),
                                              u.get('opr',''),
                                              u.get('partition_id',''),
                                              u.get('dimmer_name',''),
                                              u.get('status',''),
                                              u.get('node_id',''),
                                              u.get('level',''),
                                              u.get('created_by',''),
                                              u.get('created_date',''),
                                              u.get('updated_by',''),
                                              u.get('last_updated_date',''),
                                              u.get('endpoint',''),
                                              u.get('power_details',''),
                                              u.get('paired_status',''))

                case self.URI_DoorLocksContentProvider:
                    continue

                case self.URI_EUEventContentProvider:
                    continue

                case self.URI_HeatMapContentProvider:
                    for u in uri.get('resultSet'):
                        self.add_heat_map(u.get('_id',''),
                                             u.get('version',''),
                                             u.get('opr',''),
                                             u.get('partition_id',''),
                                             u.get('userid',''),
                                             u.get('fragment_id',''),
                                             u.get('element_id',''),
                                             u.get('count',''),
                                             u.get('time_stamp',''))
                                    
                # HistoryContentProvider                
                case self.URI_HistoryContentProvider:
                    for u in uri.get('resultSet'):
                        self.add_history(_id = u.get('_id'),
                                            version = u.get('version',''),
                                            opr = u.get('opr',''),
                                            partition_id = u.get('partition_id',''),
                                            device = u.get('device',''),
                                            events = u.get('events',''),
                                            time = u.get('time',''),
                                            ack = u.get('ack',''),
                                            type = u.get('type',''),
                                            feature1 = u.get('feature1',''),
                                            device_id = u.get('device_id',''))

                case self.URI_IQRemoteSettingsContentProvider:
                    continue

                case self.URI_SceneContentProvider:
                    continue

                case self.URI_MasterSlaveContentProvider:
                    for u in uri.get('resultSet'):
                        self.add_master_slave(u.get('_id'),u.get('version',''),u.get('opr',''),u.get('partition_id',''),u.get('zone_id',''),u.get('ip_address',''),u.get('mac_address',''),u.get('device_type',''),u.get('created_by',''),u.get('created_date',''),u.get('updated_by',''),u.get('last_upgraded_date',''),u.get('status',''),u.get('device_name',''),u.get('last_updated_iq_remote_checksum',''),u.get('software_version',''),u.get('upgraded_status',''),u.get('name',''),u.get('bssid',''),u.get('dhcpInfo',''),u.get('topology',''))

                # SettingsProvider
                case self.URI_SettingsProvider:
                    for s in uri.get('resultSet'):
                        self.add_setting(_id = s.get('_id'),
                                            version = s.get('version',''),
                                            opr = s.get('opr',''),
                                            partition_id = s.get('partition_id',''),
                                            name = s.get('name',''),
                                            value = s.get('value',''))

                case self.URI_SmartSocketsContentProvider:
                    continue

                case self.URI_TccContentProvider:
                    continue

                # ThermostatsContentProvider
                case self.URI_ThermostatsContentProvider:
                    for t in uri.get('resultSet'):
                        self.add_thermostat( _id = t.get('_id',''),
                                                version= t.get('version',''),
                                                opr = t.get('opr',''),
                                                partition_id = t.get('partition_id',''),
                                                thermostat_id = t.get('thermostat_id',''),
                                                thermostat_name = t.get('thermostat_name',''),
                                                current_temp = t.get('current_temp',''),
                                                target_cool_temp = t.get('target_cool_temp',''),
                                                target_heat_temp = t.get('target_heat_temp',''),
                                                target_temp = t.get('target_temp',''),
                                                power_usage = t.get('power_usage',''),
                                                thermostat_mode = t.get('thermostat_mode',''),
                                                thermostat_mode_bitmask = t.get('thermostat_mode_bitmask',''),
                                                fan_mode = t.get('fan_mode',''),
                                                fan_mode_bitmask = t.get('fan_mode_bitmask',''),
                                                set_point_mode = t.get('set_point_mode',''),
                                                set_point_mode_bitmask = t.get('set_point_mode_bitmask',''),
                                                node_id = t.get('node_id',''),
                                                created_by = t.get('created_by',''),
                                                created_date = t.get('created_date',''),
                                                updated_by = t.get('updated_by',''),
                                                last_updated_date = t.get('last_update_date',''),
                                                thermostat_mode_updated_time = t.get('thermostat_mode_updated_time',''),
                                                fan_mode_updated_time = t.get('fan_mode_updated_time',''),
                                                set_point_mode_updated_time = t.get('set_point_mode_updated_time',''),
                                                target_cool_temp_updated_time = t.get('target_cool_temp_updated_time',''),
                                                target_heat_temp_updated_time = t.get('target_heat_temp_updated_time',''),
                                                current_temp_updated_time = t.get('current_temp_updated_time',''),
                                                device_temp_unit = t.get('device_temp_unit',''),
                                                endpoint = t.get('endpoint',''),
                                                paired_status = t.get('paired_status',''),
                                                configuration_parameter = t.get('configuration_parameter',''))

                case self.URI_TroubleConditionsContentProvider:
                    continue
                
                # UserContentProvider
                case self.URI_UserContentProvider:
                    for u in  uri.get('resultSet'):
                        self.add_user(_id = u.get('_id',''),
                                         version = u.get('version',''),
                                         opr = u.get('opr',''),
                                         partition_id = u.get('partition_id',''),
                                         username = u.get('username',''),
                                         userPin = u.get('userPin',''),
                                         expirydate = u.get('expirydate',''),
                                         usertype = u.get('usertype',''),
                                         userid = u.get('userid',''),
                                         lastname = u.get('lastname',''),
                                         check_in = u.get('check_in',''),
                                         hash_user = u.get('hash_user',''))

                case self.URI_VirtualDeviceContentProvider:
                    continue

                # ZwaveContentProvider
                case self.URI_ZwaveContentProvider:
                    for u in uri.get('resultSet'):
                        self.add_zwave_node(u.get('_id'),
                                            u.get('version',''),
                                            u.get('opr',''),
                                            u.get('parition_id',''),
                                            u.get('node_id',''),
                                            u.get('node_name',''),
                                            u.get('node_type',''),
                                            u.get('node_status',''),
                                            u.get('node_secure_cmd_cls',''),
                                            u.get('node_battery_level',''),
                                            u.get('node_battery_level_value',''),
                                            u.get('is_node_listenning_node',''),
                                            u.get('basic_report_value',''),
                                            u.get('switch_multilevel_report_value',''),
                                            u.get('basic_device_type',''),
                                            u.get('generic_device_type',''),
                                            u.get('specific_device_type',''),
                                            u.get('num_secure_command_class',''),
                                            u.get('secure_command_class',''),
                                            u.get('manifacture_id',''),
                                            u.get('product_type',''),
                                            u.get('product_id',''),
                                            u.get('library_type_version',''),
                                            u.get('protocol_version',''),
                                            u.get('protocol_sub_version',''),
                                            u.get('application_version',''),
                                            u.get('application_sub_version',''),
                                            u.get('capability',''),
                                            u.get('command_class_list',''),
                                            u.get('lenof_command_class_list',''),
                                            u.get('security',''),
                                            u.get('library_type',''),
                                            u.get('last_updated_date',''),
                                            u.get('node_battery_level_updated_time',''),
                                            u.get('basic_report_updated_time',''),
                                            u.get('switch_multilevel_report_updated_time',''),
                                            u.get('multi_channel_details',''),
                                            u.get('rediscover_status',''),
                                            u.get('last_rediscover_time',''),
                                            u.get('neighbour_info',''),
                                            u.get('last_node_test_time',''),
                                            u.get('endpoint',''),
                                            u.get('endpoint_details',''),
                                            u.get('device_wakeup_time',''),
                                            u.get('role_type',''),
                                            u.get('is_sleeping_device',''),
                                            u.get('counter_passed',''),
                                            u.get('counter_failed',''),
                                            u.get('group_id',''),
                                            u.get('command_class_version',''),
                                            u.get('paired_status',''),
                                            u.get('device_dsk',''),
                                            u.get('endpoint_secure_command_class',''),
                                            u.get('s2_security_key',''),
                                            u.get('device_protocol',''),
                                            u.get('id_device_hidden',''))
                        
                # ZDeviceHistoryContentProvider
                case self.URI_ZDeviceHistoryContentProvider:
                    for u in uri.get('resultSet'):
                        self.add_zwave_history(u.get('_id'),
                                               u.get('version',''),
                                               u.get('opr',''),
                                               u.get('partition_id',''),
                                               u.get('node_id',''),
                                               u.get('device_name',''),
                                               u.get('source',''),
                                               u.get('event',''),
                                               u.get('request',''),
                                               u.get('response',''),
                                               u.get('created_date',''),
                                               u.get('updated_date',''),
                                               u.get('last_updated_by',''),
                                               u.get('field_type',''),
                                               u.get('ack',''),
                                               u.get('protocol',''))
                        
                #AutomationDeviceContentProvider
                case self.URI_AutomationDeviceContentProvider:
                    for u in uri.get('resultSet'):
                        self.add_automation(u.get('_id'),
                                            u.get('virtual_node_id',''),
                                            u.get('version',''),
                                            u.get('opr',''),
                                            u.get('partition_id',''),
                                            u.get('end_point',''),
                                            u.get('extra',''),
                                            u.get('is_autolocking_enabled',''),
                                            u.get('device_type',''),
                                            u.get('endpoint_secure_cmd_classes',''),
                                            u.get('automation_id',''),
                                            u.get('device_name',''),
                                            u.get('protocol',''),
                                            u.get('node_battery_level_value',''),
                                            u.get('state',''),
                                            u.get('last_updated_date',''),
                                            u.get('manufacturer_id',''),
                                            u.get('endpoint_cmd_classes',''),
                                            u.get('device_id',''),
                                            u.get('nodeid_cmd_classes',''),
                                            u.get('is_device_hidden',''),
                                            u.get('nodeid_cmd_classes',''),
                                            u.get('created_date',''),
                                            u.get('status',''))
                case _:
                    pass
                    #LOGGER.debug(f'Unknown URI in IQ2MEID Database: {uri.get('uri')}')

    def _create_db(self):
        
        #Create PartitionContentProvider table
        self.cursor.execute('''
            CREATE TABLE partition (
                _id TEXT PRIMARY KEY,
                version TEXT,
                opr TEXT,
                partition_id TEXT,
                name TEXT,
                devices TEXT
            )
        ''')

        # Create SensorContentProvider table
        self.cursor.execute('''
            CREATE TABLE sensor (
                _id TEXT PRIMARY KEY,
                version TEXT,
                opr TEXT,
                partition_id TEXT,
                ac_status TEXT,
                sensorid TEXT,
                sensortype TEXT,
                sensorname TEXT,
                sensorgroup TEXT,
                chimetype TEXT,
                sensorstatus TEXT,
                time TEXT,
                sensorstate TEXT,
                sensortts TEXT,
                zoneid TEXT,
                frame_id TEXT,
                zone_alarm_type TEXT,
                zone_equipment_code TEXT,
                zone_physical_type TEXT,
                zone_type TEXT,
                zone_rf_sensor TEXT,
                zone_supervised TEXT,
                zone_two_way_voice_enabled TEXT,
                zone_reporting_enabled TEXT,
                battery_status TEXT,
                created_date TEXT,
                created_by TEXT,
                updated_date TEXT,
                updated_by TEXT,
                frame_count TEXT,
                frame_type TEXT,
                current_capability TEXT,
                shortID TEXT,
                diag_24hr TEXT,
                allowdisarming TEXT,
                device_capability TEXT,
                sub_type TEXT,
                signal_source TEXT,
                powerg_manufacture_id TEXT,
                parent_node TEXT,
                latestdBm TEXT,
                averagedBm TEXT,
                serial_number TEXT,
                extras TEXT                   
            )
        ''')

        #Create QolsysSettingsProvider table
        self.cursor.execute('''
            CREATE TABLE qolsyssettings (
                _id TEXT PRIMARY KEY,
                version TEXT,
                opr TEXT,
                partition_id TEXT,
                name TEXT,
                value TEXT
            )
        ''')

        #Create StateContentProvider table
        self.cursor.execute('''
            CREATE TABLE state (
                _id TEXT PRIMARY KEY,
                version TEXT,
                opr TEXT,
                partition_id TEXT,
                name TEXT,
                value TEXT,
                extraparams TEXT
            )
        ''')

        #Create ThermostatsContentProvider table
        self.cursor.execute('''
            CREATE TABLE thermostat (
                _id TEXT PRIMARY KEY,
                version TEXT,
                opr TEXT,
                partition_id TEXT,
                thermostat_id TEXT,
                thermostat_name TEXT,
                current_temp TEXT,
                target_cool_temp TEXT,
                target_heat_temp TEXT,
                target_temp TEXT,
                power_usage TEXT,
                thermostat_mode TEXT,
                thermostat_mode_bitmask TEXT,
                fan_mode TEXT,
                fan_mode_bitmask TEXT,
                set_point_mode TEXT,
                set_point_mode_bitmask TEXT,
                node_id TEXT,
                created_by TEXT,
                created_date TEXT,
                updated_by TEXT,
                last_updated_date TEXT,
                thermostat_mode_updated_time TEXT,
                fan_mode_updated_time TEXT,
                set_point_mode_updated_time TEXT,
                target_cool_temp_updated_time TEXT,
                target_heat_temp_updated_time TEXT,
                current_temp_updated_time TEXT,
                device_temp_unit TEXT,
                endpoint TEXT,                               
                paired_status TEXT,
                configuration_parameter TEXT                                        
            )
        ''')

        #Create UserContentProvider table
        self.cursor.execute('''
            CREATE TABLE user (
                _id TEXT PRIMARY KEY,
                version TEXT,
                opr TEXT,
                partition_id TEXT,
                username TEXT,
                userPin TEXT,  
                expirydate TEXT,
                usertype TEXT,
                userid TEXT,
                lastname TEXT,
                check_in TEXT,
                hash_user TEXT    
            )
        ''')

        #Create HistoryContentProvider table
        self.cursor.execute('''
            CREATE TABLE history (
                _id TEXT PRIMARY KEY,
                version TEXT,
                opr TEXT,
                partition_id TEXT,
                device TEXT,
                events TEXT,  
                time TEXT,
                ack TEXT,
                type TEXT,
                feature1 TEXT,
                device_id TEXT
            )
        ''')

        #Create HeatMapContentProvider table
        self.cursor.execute('''
            CREATE TABLE heat_map (
                _id TEXT PRIMARY KEY,
                version TEXT,
                opr TEXT,
                partition_id TEXT,
                userid TEXT,
                fragment_id TEXT,
                element_id TEXT,
                count TEXT,
                time_stamp TEXT
            )
        ''')

        #Create AlarmedSensorProvider table
        self.cursor.execute('''
            CREATE TABLE alarmedsensor (
                _id TEXT PRIMARY KEY,
                partition_id TEXT,
                silenced TEXT,
                zone_id TEXT,
                sgroup TEXT,
                action TEXT,
                timed_out TEXT,
                type TEXT,
                priority TEXT,
                aseb_type TEXT
            )
        ''')

        #Create MasterSlaveContentProvider table
        self.cursor.execute('''
            CREATE TABLE master_slave (
                _id TEXT PRIMARY KEY,
                version TEXT,
                opr TEXT,
                partition_id TEXT,
                zone_id TEXT,
                ip_address TEXT,
                mac_address TEXT,
                device_type TEXT,
                created_by TEXT,
                created_date TEXT,
                updated_by TEXT,
                last_updated_date TEXT,
                status TEXT,
                device_name TEXT,
                last_updated_iq_remote_checksum TEXT, 
                software_version TEXT,   
                upgrade_status TEXT,
                name TEXT,
                bssid TEXT,
                dhcpInfo TEXT,
                topology TEXT
            )
        ''')

        #Create dashboard_msgs table
        self.cursor.execute('''
            CREATE TABLE dashboard_msgs (
                _id TEXT PRIMARY KEY,
                version TEXT,
                opr TEXT,
                partition_id TEXT,
                msg_id TEXT,
                title TEXT,
                description TEXT,
                received_time TEXT,
                start_time TEXT,
                end_time TEXT,
                read TEXT,
                mime_type TEXT
            )
        ''')

        #Create zwave_node table
        self.cursor.execute('''
            CREATE TABLE zwave_node (
                _id TEXT PRIMARY KEY,
                version TEXT,
                opr TEXT,
                partition_id TEXT,
                node_id TEXT,
                node_name TEXT,
                node_type TEXT,
                node_status TEXT,
                node_secure_cmd_cls TEXT,
                node_battery_level TEXT,
                node_battery_level_value TEXT,
                is_node_listening_node TEXT,             
                basic_report_value TEXT,
                switch_multilevel_report_value TEXT,
                basic_device_type TEXT,
                generic_device_type TEXT,
                specific_device_type TEXT,
                num_secure_command_class TEXT,
                secure_command_class TEXT,
                manufacture_id TEXT,
                product_type TEXT,
                product_id TEXT,
                library_type_version TEXT,
                protocol_version TEXT,
                protocol_sub_version TEXT,
                application_version TEXT,
                application_sub_version TEXT,
                capability TEXT,
                command_class_list TEXT,        
                lenof_command_class_list TEXT,
                security TEXT,
                library_type TEXT,
                last_updated_date TEXT,       
                node_battery_level_updated_time TEXT,
                basic_report_updated_time TEXT,
                switch_multilevel_report_updated_time TEXT,
                multi_channel_details TEXT,
                rediscover_status TEXT,
                last_rediscover_time TEXT,
                neighbour_info TEXT,
                last_node_test_time TEXT,
                endpoint TEXT,          
                endpoint_details TEXT,
                device_wakeup_time TEXT,
                role_type TEXT,
                is_device_sleeping TEXT,
                counters_passed TEXT,
                counters_failed TEXT,
                group_id TEXT,
                command_classes_version TEXT,
                paired_status TEXT,
                device_dsk TEXT,
                endpoint_secure_cmd_cls TEXT,
                s2_security_keys TEXT,
                device_protocol TEXT,
                is_device_hidden TEXT
            )
        ''')

        #Create dimmerlight table
        self.cursor.execute('''
            CREATE TABLE dimmerlight (
                _id TEXT PRIMARY KEY,
                version TEXT,
                opr TEXT,
                partition_id TEXT,
                dimmer_name TEXT,
                status TEXT,
                node_id TEXT,
                level TEXT,
                created_by TEXT,
                created_date TEXT,
                updated_by TEXT,
                last_updated_date TEXT,
                endpoint TEXT,
                power_details TEXT,
                paired_status TEXT
            )
        ''')

        #Create zwave_history table
        self.cursor.execute('''
            CREATE TABLE zwave_history (
                _id TEXT PRIMARY KEY,
                version TEXT,
                opr TEXT,
                partition_id TEXT,
                node_id TEXT,
                device_name TEXT,
                source TEXT,
                event TEXT,
                request TEXT,
                response TEXT,
                created_date TEXT,
                updated_date TEXT,
                last_updated_by TEXT,
                field_type TEXT,
                ack TEXT,
                protocol TEXT
            )
        ''')

        #Create automation table
        self.cursor.execute('''
            CREATE TABLE automation (
                _id TEXT PRIMARY KEY,
                virtual_node_id TEXT,
                version TEXT,
                opr TEXT,
                partition_id TEXT,
                end_point TEXT,
                extras TEXT,
                is_autolocking_enabled TEXT,
                device_type TEXT,
                endpoint_secure_cmd_classes TEXT,
                automation_id TEXT,
                device_name TEXT,
                protocol TEXT,
                node_battery_level_value TEXT,
                state TEXT,
                last_updated_date TEXT,
                manufacturer_id TEXT,
                endpoint_cmd_classes TEXT,
                device_id TEXT,
                nodeid_cmd_classes TEXT,
                is_device_hidden TEXT,
                nodeid_secure_cmd_classes TEXT,
                created_date TEXT,
                status TEXT
            )
        ''')

        self.db.commit()

    def db_show(self):
        print('\n')
        t = PrettyTable(['partition_id', 'name'])
        self.cursor.execute(f"SELECT partition_id,name FROM {self.Table_PartitionContentProvider}")
        t.add_rows(self.cursor.fetchall())
        print("Content of 'PartitionContentProvider' table:")
        print(t)

        print('\n')
        t = PrettyTable(['zoneid','partition_id', 'sensorname','sensorgroup','sensorstatus','lastestdBm','battery_status','time'])
        self.cursor.execute(f"SELECT zoneid,partition_id, sensorname, sensorgroup, sensorstatus, latestdBm, battery_status, time FROM {self.Table_SensorContentProvider} ORDER BY zoneid")
        t.add_rows(self.cursor.fetchall())
        print("Content of 'SensorContentProvider' table:")
        print(t)

        print('\n')
        t = PrettyTable(['userid','partition_id', 'username','lastname','userPin'])
        self.cursor.execute(f"SELECT userid,partition_id,username,lastname,userPin FROM {self.Table_UserContentProvider}")
        t.add_rows(self.cursor.fetchall())
        print("Content of 'UserContentProvider' table:")
        print(t)

        print('\n')
        t = PrettyTable(['_id', 'name', 'partition_id', 'value'])
        self.cursor.execute(f"SELECT _id,name,partition_id,value FROM {self.Table_QolsysSettingsProvider}")
        t.add_rows(self.cursor.fetchall())
        print("Content of 'QolsysSettingsProvider' table:")
        print(t)

        print('\n')
        t = PrettyTable(['_id', 'partition_id','name', 'value'])
        self.cursor.execute(f"SELECT _id,partition_id,name,value FROM {self.Table_StateContentProvider}")
        t.add_rows(self.cursor.fetchall())
        print("Content of 'StateContentProvider' table:")
        print(t)

        print('\n')
        t = PrettyTable(['thermostat_id','partition_id', 'thermostat_name','current_temp'])
        self.cursor.execute(f"SELECT thermostat_id,partition_id,thermostat_name,current_temp FROM {self.Table_ThermostatsContentProvider}")
        t.add_rows(self.cursor.fetchall())
        print("Content of 'ThermostatsContentProvider' table:")
        print(t)

        print('\n')
        t = PrettyTable(['_id','partition_id','device', 'events','type', 'device_id'])
        self.cursor.execute(f"SELECT _id,partition_id,device,events,type, device_id FROM {self.Table_HistoryContentProvider}")
        t.add_rows(self.cursor.fetchall())
        print("Content of 'HistoryContentProvider' table:")
        print(t)

        print('\n')
        
        t = PrettyTable(['_id','partition_id','fragment_id', 'element_id'])
        self.cursor.execute(f"SELECT _id,partition_id,fragment_id,element_id FROM {self.Table_HeatMapContentProvider}")
        t.add_rows(self.cursor.fetchall())
        print("Content of 'HeatMapContentProvider' table:")
        print(t)
        
        t = PrettyTable(['_id','partition_id','zone_id', 'sgroup','priority','action','type'])
        self.cursor.execute(f"SELECT _id,partition_id,zone_id,sgroup,priority,action,type FROM {self.Table_AlarmedSensorProvider}")
        t.add_rows(self.cursor.fetchall())
        print("Content of 'AlarmedSensorProvider' table:")
        print(t)

        t = PrettyTable(['_id','partition_id','zone_id', 'name','mac_address'])
        self.cursor.execute(f"SELECT _id,partition_id,zone_id,name,mac_address FROM {self.Table_MasterSlaveContentProvider}")
        t.add_rows(self.cursor.fetchall())
        print("Content of 'master_slave' table:")
        print(t)

        print('\n')






            


    


