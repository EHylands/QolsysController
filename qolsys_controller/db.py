import logging
import sqlite3

LOGGER = logging.getLogger(__name__)

class QolsysDB:

    def __init__(self) -> None:
        self.Table_QolsysSettingsProvider = "qolsyssettings"
        self.Table_SensorContentProvider = "sensor"
        self.Table_StateContentProvider = "state"
        self.Table_UserContentProvider = "user"
        self.Table_HeatMapContentProvider = "heat_map"
        self.Table_AlarmedSensorProvider = "alarmedsensor"
        self.Table_HistoryContentProvider = "history"
        self.Table_MasterSlaveContentProvider = "master_slave"
        self.Table_DashboardMessagesContentProvider = "dashboard_msgs"
        self.Table_PartitionContentProvider = "partition"
        self.Table_ThermostatsContentProvider = "thermostat"
        self.Table_ZwaveContentProvider = "zwave_node"
        self.Table_DimmerLightsContentProvider = "dimmerlight"
        self.Table_ZDeviceHistoryContentProvider = "zwave_history"
        self.Table_AutomationDeviceContentProvider = "automation"
        self.Table_IQRemoteSettingsContentProvider = "iqremotesettings"
        self.Table_DoorLocksContentProvider = "doorlock"

        self.URI_AutomationDeviceContentProvider = "content://com.qolsys.qolsysprovider.AutomationDeviceContentProvider/automation"
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
        self.URI_IQRemoteSettingsContentProvider = "content://com.qolsys.qolsysprovider.IQRemoteSettingsContentProvider/iqremotesettings"
        self.URI_DoorLocksContentProvider = "content://com.qolsys.qolsysprovider.DoorLocksContentProvider/doorlock"
        self.URI_SmartSocketsContentProvider = "content://com.qolsys.qolsysprovider.SmartSocketsContentProvider/smartsocket"
        self.URI_SceneContentProvider = "content://com.qolsys.qolsysprovider.SceneContentProvider/scene"
        self.URI_ZDeviceHistoryContentProvider = "content://com.qolsys.qolsysprovider.ZDeviceHistoryContentProvider/zwave_history"

        self._db = sqlite3.connect(":memory:")
        self._cursor = self._db.cursor()
        self._create_db()

    @property
    def db(self):
        return self._db

    @property
    def cursor(self):
        return self._cursor

    def delete_table(self,table:str,selection:str,selection_argument:str) -> None:
        # Selection Argument
        selection_argument = selection_argument.replace("[","")
        selection_argument = selection_argument.replace("]","")
        selection_argument = selection_argument.split(",")

        # Replace '?' in selection string with selectio_argument
        for i in selection_argument:
            selection = selection.replace("?",f"'{i}'",1)

        query = f"DELETE FROM {table} WHERE {selection}"
        self.cursor.execute(query)
        self.db.commit()

    def update_table(self,table:str,selection:str,selection_argument:str,new_value:str) -> None:
        # Panel is sending query parameter for db update in text string
        # Have not found a way to make it work with parametrized query yet
        # Using f string concat for moment ...

        # New Values to update in table
        db_value = []
        for key, value in new_value.items():
            db_value.append(f"{key}=\'{value}\'")
        db_value = ",".join(db_value)

        # Selection Argument
        selection_argument = selection_argument.replace("[","")
        selection_argument = selection_argument.replace("]","")
        selection_argument = selection_argument.split(",")

        for i in selection_argument:
            selection = selection.replace("?",f"\'{i}\'",1)

         # Final query
        query = f"UPDATE {table} SET {db_value} WHERE {selection}"

        self.cursor.execute(query)
        self.db.commit()

    def get_partitions(self) -> list[dict]:
        self.cursor.execute(f"SELECT * FROM {self.Table_PartitionContentProvider} ORDER BY partition_id" )
        self.db.commit()

        partitions = []
        columns = [description[0] for description in self.cursor.description]
        for row in  self.cursor.fetchall():
            row_dict = dict(zip(columns, row, strict=True))
            partitions.append(row_dict)

        return partitions

    def get_zwave_devices(self) -> list[dict]:
        self.cursor.execute(f"SELECT * FROM {self.Table_ZwaveContentProvider} ORDER BY node_id" )
        self.db.commit()

        devices = []
        columns = [description[0] for description in self.cursor.description]
        for row in  self.cursor.fetchall():
            row_dict = dict(zip(columns, row, strict=True))
            devices.append(row_dict)

        return devices

    def get_locks(self) -> list[dict]:
        self.cursor.execute(f"SELECT * FROM {self.Table_DoorLocksContentProvider} ORDER BY node_id" )
        self.db.commit()

        locks = []
        columns = [description[0] for description in self.cursor.description]
        for row in  self.cursor.fetchall():
            row_dict = dict(zip(columns, row, strict=True))
            locks.append(row_dict)

        return locks

    def get_thermostats(self) -> list[dict]:
        self.cursor.execute(f"SELECT * FROM {self.Table_ThermostatsContentProvider} ORDER BY node_id" )
        self.db.commit()

        thermostats = []
        columns = [description[0] for description in self.cursor.description]
        for row in  self.cursor.fetchall():
            row_dict = dict(zip(columns, row, strict=True))
            thermostats.append(row_dict)

        return thermostats

    def get_dimmers(self) -> list[dict]:
        self.cursor.execute(f"SELECT * FROM {self.Table_DimmerLightsContentProvider} ORDER BY node_id" )
        self.db.commit()

        dimmers = []
        columns = [description[0] for description in self.cursor.description]
        for row in  self.cursor.fetchall():
            row_dict = dict(zip(columns, row, strict=True))
            dimmers.append(row_dict)

        return dimmers

    def get_zones(self) -> list[dict]:
        self.cursor.execute(f"SELECT * FROM {self.Table_SensorContentProvider} ORDER BY zoneid" )
        self.db.commit()

        zones = []
        columns = [description[0] for description in self.cursor.description]
        for row in  self.cursor.fetchall():
            row_dict = dict(zip(columns, row, strict=True))
            zones.append(row_dict)

        return zones

    def get_setting_panel(self,setting:str):
        self.cursor.execute(f"SELECT value FROM {self.Table_QolsysSettingsProvider} WHERE name = ? and partition_id  = ? ", (setting,"0"))
        row = self.cursor.fetchone()

        if row is None:
            LOGGER.error("%s value not found",setting)

        return row[0]

    def get_setting_partition(self,setting:str,partition_id:str):
        self.cursor.execute(f"SELECT value FROM {self.Table_QolsysSettingsProvider} WHERE name = ? and partition_id  = ? ", (setting,partition_id))
        row = self.cursor.fetchone()

        if row is None:
            LOGGER.error("%s value not found",setting)

        return row[0]

    def get_state_partition(self,state:str,partition_id:str):
        self.cursor.execute(f"SELECT value FROM {self.Table_StateContentProvider} WHERE name = ? and partition_id  = ? ", (state,partition_id))
        row = self.cursor.fetchone()

        if row is None:
            LOGGER.error("%s value not found",state)

        return row[0]

    def get_alarm_type(self,partition_id:str) -> list[str]:
        alarm_type = []
        self.cursor.execute(f"SELECT sgroup FROM {self.Table_AlarmedSensorProvider} WHERE partition_id  = ? ", (partition_id))
        rows = self.cursor.fetchall()

        for row in rows:
            alarm_type.append(row[0])

        return alarm_type

    def add_state(self,data:dict) -> None:
        self.cursor.execute(f"INSERT INTO {self.Table_StateContentProvider} (_id,version,opr,partition_id,name,value,extraparams) VALUES (?,?,?,?,?,?,?)",(
            data.get("_id"),
            data.get("version",""),
            data.get("opr",""),
            data.get("partition_id",""),
            data.get("name",""),
            data.get("value"),
            data.get("extraparams","")))

        self.db.commit()

    def add_partition(self,data:dict) -> None:
        self.cursor.execute(f"INSERT INTO {self.Table_PartitionContentProvider} (_id,version,opr,partition_id,name,devices) VALUES (?,?,?,?,?,?)",(
            data.get("_id"),
            data.get("version",""),
            data.get("opr",""),
            data.get("partition_id",""),
            data.get("name",""),
            data.get("devices","")))

        self.db.commit()

    def add_setting(self,data:dict) -> None:
        self.cursor.execute(f"INSERT INTO {self.Table_QolsysSettingsProvider} (_id,version,opr,partition_id,name,value) VALUES (?,?,?,?,?,?)",(
            data.get("_id"),
            data.get("version",""),
            data.get("opr",""),
            data.get("partition_id",""),
            data.get("name",""),
            data.get("value","")))

        self.db.commit()

    def add_sensor(self,data:dict) -> None:
        self.cursor.execute(f"INSERT INTO {self.Table_SensorContentProvider} (_id,version,opr,partition_id,sensorid,sensortype,sensorname,sensorgroup,chimetype,sensorstatus,time,sensorstate,sensortts,zoneid,frame_id,zone_alarm_type,zone_equipment_code,zone_physical_type,zone_type,zone_rf_sensor,zone_supervised,zone_two_way_voice_enabled, zone_reporting_enabled, battery_status,created_date,created_by,updated_date,updated_by,frame_count,frame_type,current_capability,shortID,diag_24hr,allowdisarming,device_capability,sub_type, signal_source, powerg_manufacture_id,parent_node,latestdBm,averagedBm,serial_number,extras,ac_status) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(
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

        self.db.commit()

    def add_zwave_node(self,data:dict) -> None:
        self.cursor.execute(f"""INSERT INTO {self.Table_ZwaveContentProvider} (_id,version,opr,partition_id,node_id,node_name,node_type,node_status,node_secure_cmd_cls,node_battery_level,
                            node_battery_level_value,is_node_listening_node,basic_report_value,switch_multilevel_report_value,basic_device_type,generic_device_type,
                            specific_device_type,num_secure_command_class,secure_command_class,manufacture_id,product_type,product_id,library_type_version,protocol_version,
                            protocol_sub_version,application_version,application_sub_version,capability,command_class_list,lenof_command_class_list,security,
                            library_type,last_updated_date,node_battery_level_updated_time,basic_report_updated_time,switch_multilevel_report_updated_time,
                            multi_channel_details,rediscover_status,last_rediscover_time,neighbour_info,last_node_test_time,endpoint,endpoint_details,device_wakeup_time,
                            role_type,is_device_sleeping,counters_passed,counters_failed,group_id,command_classes_version,paired_status,device_dsk,endpoint_secure_cmd_cls,
                            s2_security_keys,device_protocol,is_device_hidden,ime_data) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",(
                            data.get("_id"),
                            data.get("version",""),
                            data.get("opr",""),
                            data.get("partition_id",""),
                            data.get("node_id",""),
                            data.get("node_name",""),
                            data.get("node_type",""),
                            data.get("node_status",""),
                            data.get("node_secure_cmd_cls",""),
                            data.get("node_battery_level",""),
                            data.get("node_battery_level_value",""),
                            data.get("is_node_listening_node",""),
                            data.get("basic_report_value",""),
                            data.get("switch_multilevel_report_value",""),
                            data.get("basic_device_type",""),
                            data.get("generic_device_type",""),
                            data.get("specific_device_type",""),
                            data.get("num_secure_command_class",""),
                            data.get("secure_command_class",""),
                            data.get("manufacture_id",""),
                            data.get("product_type",""),
                            data.get("product_id",""),
                            data.get("library_type_version",""),
                            data.get("protocol_version",""),
                            data.get("protocol_sub_version",""),
                            data.get("application_version",""),
                            data.get("application_sub_version",""),
                            data.get("capability",""),
                            data.get("command_class_list",""),
                            data.get("lenof_command_class_list",""),
                            data.get("security",""),
                            data.get("library_type",""),
                            data.get("last_updated_date",""),
                            data.get("node_battery_level_updated_time",""),
                            data.get("basic_report_updated_time",""),
                            data.get("switch_multilevel_report_updated_time",""),
                            data.get("multi_channel_details",""),
                            data.get("rediscover_status",""),
                            data.get("last_rediscover_time",""),
                            data.get("neighbour_info",""),
                            data.get("last_node_test_time",""),
                            data.get("endpoint",""),
                            data.get("endpoint_details",""),
                            data.get("device_wakeup_time",""),
                            data.get("role_type",""),
                            data.get("is_device_sleeping",""),
                            data.get("counters_passed",""),
                            data.get("counters_failed",""),
                            data.get("group_id",""),
                            data.get("command_classes_version",""),
                            data.get("paired_status",""),
                            data.get("device_dsk",""),
                            data.get("endpoint_secure_cmd_cls",""),
                            data.get("s2_security_keys",""),
                            data.get("device_protocol",""),
                            data.get("is_device_hidden",""),
                            data.get("ime_data","")))

        self.db.commit()

    def add_zwave_history(self,data:dict) -> None:
        self.cursor.execute(f"INSERT INTO {self.Table_ZDeviceHistoryContentProvider} (_id,version,opr,partition_id,node_id,device_name,source,event,request,response,created_date,updated_date,last_updated_by,field_type,ack,protocol) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(
            data.get("_id"),
            data.get("version",""),
            data.get("opr",""),
            data.get("partition_id",""),
            data.get("node_id",""),
            data.get("device_name",""),
            data.get("source",""),
            data.get("event",""),
            data.get("request",""),
            data.get("response",""),
            data.get("created_date",""),
            data.get("updated_date",""),
            data.get("last_updated_by",""),
            data.get("field_type",""),
            data.get("ack",""),
            data.get("protocol","")))

        self.db.commit()

    def add_automation(self,data:dict) -> None :
        self.cursor.execute(f"INSERT INTO {self.Table_AutomationDeviceContentProvider} (_id,virtual_node_id,version,opr,partition_id,end_point,extras,is_autolocking_enabled,device_type,endpoint_secure_cmd_classes,automation_id,device_name,protocol,node_battery_level_value,state,last_updated_date,manufacturer_id,endpoint_cmd_classes,device_id,nodeid_cmd_classes,is_device_hidden,nodeid_secure_cmd_classes,created_date,status) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(
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

        self.db.commit()

    def add_dimmer_light(self,data:dict) -> None:
        self.cursor.execute(f"INSERT INTO {self.Table_DimmerLightsContentProvider} (_id,version,opr,partition_id,dimmer_name,status,node_id,level,created_by,created_date,updated_by,last_updated_date,endpoint,power_details,paired_status) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(
                            data.get("_id"),
                            data.get("version",""),
                            data.get("opr",""),
                            data.get("partition_id",""),
                            data.get("dimmer_name",""),
                            data.get("status",""),
                            data.get("node_id",""),
                            data.get("level",""),
                            data.get("created_by",""),
                            data.get("created_date",""),
                            data.get("updated_by",""),
                            data.get("last_updated_date",""),
                            data.get("endpoint",""),
                            data.get("power_details",""),
                            data.get("paired_status","")))

        self.db.commit()

    def add_doorlock(self,data:dict) -> None:
        self.cursor.execute(f"INSERT INTO {self.Table_DoorLocksContentProvider} (_id,version,opr,partition_id,doorlock_name,status,node_id,remote_arming,keyfob_arming,panel_arming,created_by,created_date,updated_by,last_updated_date,endpoint,paired_status) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (data.get("_id"),
            data.get("version",""),
            data.get("opr",""),
            data.get("partition_id",""),
            data.get("doorlock_name",""),
            data.get("status",""),
            data.get("node_id",""),
            data.get("remote_arming",""),
            data.get("keyfob_arming",""),
            data.get("panel_arming",""),
            data.get("created_by",""),
            data.get("created_date",""),
            data.get("updated_by",""),
            data.get("last_updated_date",""),
            data.get("endpoint",""),
            data.get("paired_status","")))

        self.db.commit()

    def add_thermostat(self,data:dict) -> None:
        self.cursor.execute(f"INSERT INTO {self.Table_ThermostatsContentProvider} (_id,version,opr,partition_id,thermostat_id,thermostat_name,current_temp,target_cool_temp,target_heat_temp,target_temp,power_usage,thermostat_mode,thermostat_mode_bitmask,fan_mode,fan_mode_bitmask,set_point_mode,set_point_mode_bitmask,node_id,created_by,created_date,updated_by,last_updated_date,thermostat_mode_updated_time,fan_mode_updated_time,set_point_mode_updated_time,target_cool_temp_updated_time,target_heat_temp_updated_time,current_temp_updated_time,device_temp_unit,endpoint,paired_status,configuration_parameter) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(
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

        self.db.commit()

    def add_user(self,data:dict) -> None:
        self.cursor.execute(f"INSERT INTO {self.Table_UserContentProvider} (_id,version,opr,partition_id,username,userPin,expirydate,usertype,userid,lastname,check_in,hash_user) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",(
            data.get("_id"),
            data.get("version",""),
            data.get("opr",""),
            data.get("partition_id",""),
            data.get("username",""),
            data.get("userPin",""),
            data.get("expirydate",""),
            data.get("usertype",""),
            data.get("userid",""),
            data.get("lastname",""),
            data.get("check_in",""),
            data.get("hash_user","")))

        self.db.commit()

    def add_history(self,data:dict) -> None:
        self.cursor.execute(f"INSERT INTO {self.Table_HistoryContentProvider} (_id,version,opr,partition_id,device,events,time,ack,type,feature1,device_id) VALUES (?,?,?,?,?,?,?,?,?,?,?)",(
            data.get("_id"),
            data.get("version",""),
            data.get("opr",""),
            data.get("partition_id",""),
            data.get("device",""),
            data.get("events",""),
            data.get("time",""),
            data.get("ack",""),
            data.get("type",""),
            data.get("feature1",""),
            data.get("device_id","")))

        self.db.commit()

    def add_heat_map(self,data:dict) -> None:
        self.cursor.execute(f"INSERT INTO {self.Table_HeatMapContentProvider} (_id,version,opr,partition_id,userid,fragment_id,element_id,count,time_stamp) VALUES (?,?,?,?,?,?,?,?,?)",(
            data.get("_id"),
            data.get("version",""),
            data.get("opr",""),
            data.get("partition_id",""),
            data.get("userid",""),
            data.get("fragment_id",""),
            data.get("element_id",""),
            data.get("count",""),
            data.get("time_stamp","")))

        self.db.commit()

    def add_alarmed_sensor(self,data:dict) -> None:
        self.cursor.execute(f"INSERT INTO {self.Table_AlarmedSensorProvider} (_id,partition_id,silenced,zone_id,sgroup,action,timed_out,type,priority,aseb_type) VALUES (?,?,?,?,?,?,?,?,?,?)",(
            data.get("_id"),
            data.get("partition_id",""),
            data.get("silenced",""),
            data.get("zone_id",""),
            data.get("sgroup",""),
            data.get("action",""),
            data.get("timed_out",""),
            data.get("type",""),
            data.get("priority",""),
            data.get("aseb_type","")))
        self.db.commit()

    def add_master_slave(self,data:dict) -> None:
        self.cursor.execute(f"INSERT INTO {self.Table_MasterSlaveContentProvider} (_id,version,opr,partition_id,zone_id,ip_address,mac_address,device_type,created_by,created_date,updated_by,last_updated_date,status,device_name,last_updated_iq_remote_checksum,software_version,upgrade_status,name,bssid,dhcpInfo,topology) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(
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

        self.db.commit()

    def add_iqremotesettings(self,data:dict) -> None:
        self.cursor.execute(f"INSERT INTO {self.Table_IQRemoteSettingsContentProvider} (_id,version,opr,partition_id,zone_id,mac_address,name,value) VALUES (?,?,?,?,?,?,?,?)",(
            data.get("_id"),
            data.get("version",""),
            data.get("opr",""),
            data.get("partition_id",""),
            data.get("zone_id",""),
            data.get("mac_address",""),
            data.get("name",""),
            data.get("value","")))

        self.db.commit()

    def add_dashboard_msg(self,data:dict) -> None:
        self.cursor.execute(f"INSERT INTO {self.Table_DashboardMessagesContentProvider} (_id,version,opr,partition_id,msg_id,title,description,received_time,start_time,end_time,read,mime_type) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",(
            data.get("_id"),
            data.get("version"),
            data.get("opr"),
            data.get("partition_id"),
            data.get("msg_id"),
            data.get("title"),
            data.get("description"),
            data.get("received_time"),
            data.get("start_time"),
            data.get("end_time"),
            data.get("read"),
            data.get("mime_type")))

        self.db.commit()

    def clear_db(self) -> None:
        self.cursor.execute(f"DELETE from {self.Table_AlarmedSensorProvider}")
        self.db.commit()

        self.cursor.execute(f"DELETE from {self.Table_AutomationDeviceContentProvider}")
        self.db.commit()

        self.cursor.execute(f"DELETE from {self.Table_DashboardMessagesContentProvider}")
        self.db.commit()

        self.cursor.execute(f"DELETE from {self.Table_DimmerLightsContentProvider}")
        self.db.commit()

        self.cursor.execute(f"DELETE from {self.Table_HeatMapContentProvider}")
        self.db.commit()

        self.cursor.execute(f"DELETE from {self.Table_HistoryContentProvider}")
        self.db.commit()

        self.cursor.execute(f"DELETE from {self.Table_MasterSlaveContentProvider}")
        self.db.commit()

        self.cursor.execute(f"DELETE from {self.Table_PartitionContentProvider}")
        self.db.commit()

        self.cursor.execute(f"DELETE from {self.Table_QolsysSettingsProvider}")
        self.db.commit()

        self.cursor.execute(f"DELETE from {self.Table_SensorContentProvider}")
        self.db.commit()

        self.cursor.execute(f"DELETE from {self.Table_StateContentProvider}")
        self.db.commit()

        self.cursor.execute(f"DELETE from {self.Table_ThermostatsContentProvider}")
        self.db.commit()

        self.cursor.execute(f"DELETE from {self.Table_ZDeviceHistoryContentProvider}")
        self.db.commit()

        self.cursor.execute(f"DELETE from {self.Table_ZwaveContentProvider}")
        self.db.commit()

        self.cursor.execute(f"DELETE from {self.Table_UserContentProvider}")
        self.db.commit()

        self.cursor.execute(f"DELETE from {self.Table_IQRemoteSettingsContentProvider}")
        self.db.commit()

        self.cursor.execute(f"DELETE from {self.Table_DimmerLightsContentProvider}")
        self.db.commit()

    def load_db(self,database:dict) -> None:

        self.clear_db()

        if not database:
            LOGGER.error("Loading Database Error, No Data Provided")

        for uri in database:

            match uri.get("uri"):

                # PartitionContentProvider
                case self.URI_PartitionContentProvider:
                    for u in uri.get("resultSet"):
                        self.add_partition(data=u)

                # SensorContentProvider
                case self.URI_SensorContentProvider:
                    for u in uri.get("resultSet"):
                        self.add_sensor(data=u)

                # StateContentProvider
                case self.URI_StateContentProvider:
                    for u in uri.get("resultSet"):
                        self.add_state(data=u)

                # AlarmedSensorProvider
                case self.URI_AlarmedSensorProvider:
                    for u in uri.get("resultSet"):
                        self.add_alarmed_sensor(data=u)

                # DashboardMessagesContentProvider
                case self.URI_DashboardMessagesContentProvider:
                    for u in uri.get("resultSet"):
                        self.add_dashboard_msg(data=u)

                # DimmerLightsContentProvider
                case self.URI_DimmerLightsContentProvider:
                    for u in uri.get("resultSet"):
                        self.add_dimmer_light(data=u)

                # DoorLock Content Proviver
                case self.URI_DoorLocksContentProvider:
                    for u in uri.get("resultSet"):
                        self.add_doorlock(data=u)

                case self.URI_EUEventContentProvider:
                    continue

                case self.URI_HeatMapContentProvider:
                    for u in uri.get("resultSet"):
                        self.add_heat_map(data=u)

                # HistoryContentProvider
                case self.URI_HistoryContentProvider:
                    for u in uri.get("resultSet"):
                        self.add_history(data=u)

                case self.URI_IQRemoteSettingsContentProvider:
                    for u in uri.get("resultSet"):
                        self.add_iqremotesettings(data=u)

                case self.URI_SceneContentProvider:
                    continue

                case self.URI_MasterSlaveContentProvider:
                    for u in uri.get("resultSet"):
                        self.add_master_slave(data=u)

                # SettingsProvider
                case self.URI_SettingsProvider:
                    for u in uri.get("resultSet"):
                        self.add_setting(data = u)

                case self.URI_SmartSocketsContentProvider:
                    continue

                case self.URI_TccContentProvider:
                    continue

                # ThermostatsContentProvider
                case self.URI_ThermostatsContentProvider:
                    for u in uri.get("resultSet"):
                        self.add_thermostat(data=u)

                case self.URI_TroubleConditionsContentProvider:
                    continue

                # UserContentProvider
                case self.URI_UserContentProvider:
                    for u in  uri.get("resultSet"):
                        self.add_user(data=u)

                case self.URI_VirtualDeviceContentProvider:
                    continue

                # ZwaveContentProvider
                case self.URI_ZwaveContentProvider:
                    for u in uri.get("resultSet"):
                        self.add_zwave_node(data=u)

                # ZDeviceHistoryContentProvider
                case self.URI_ZDeviceHistoryContentProvider:
                    for u in uri.get("resultSet"):
                        self.add_zwave_history(data=u)

                #AutomationDeviceContentProvider
                case self.URI_AutomationDeviceContentProvider:
                    for u in uri.get("resultSet"):
                        self.add_automation(data=u)
                case _:
                    pass
                    #LOGGER.debug(f'Unknown URI in IQ2MEID Database: {uri.get('uri')}')  # noqa: ERA001

    def _create_db(self) -> None:

        #Create PartitionContentProvider table
        self.cursor.execute("""
            CREATE TABLE partition (
                _id TEXT PRIMARY KEY,
                version TEXT,
                opr TEXT,
                partition_id TEXT,
                name TEXT,
                devices TEXT
            )
        """)

        # Create SensorContentProvider table
        self.cursor.execute("""
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
        """)

        #Create QolsysSettingsProvider table
        self.cursor.execute("""
            CREATE TABLE qolsyssettings (
                _id TEXT PRIMARY KEY,
                version TEXT,
                opr TEXT,
                partition_id TEXT,
                name TEXT,
                value TEXT
            )
        """)

        #Create StateContentProvider table
        self.cursor.execute("""
            CREATE TABLE state (
                _id TEXT PRIMARY KEY,
                version TEXT,
                opr TEXT,
                partition_id TEXT,
                name TEXT,
                value TEXT,
                extraparams TEXT
            )
        """)

        #Create ThermostatsContentProvider table
        self.cursor.execute("""
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
        """)

        #Create UserContentProvider table
        self.cursor.execute("""
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
        """)

        #Create HistoryContentProvider table
        self.cursor.execute("""
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
        """)

        #Create HeatMapContentProvider table
        self.cursor.execute("""
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
        """)

        #Create AlarmedSensorProvider table
        self.cursor.execute("""
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
        """)

        #Create MasterSlaveContentProvider table
        self.cursor.execute("""
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
                topology TEXT,
                reboot_reason TEXT
            )
        """)

        #Create dashboard_msgs table
        self.cursor.execute("""
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
        """)

        #Create zwave_node table
        self.cursor.execute("""
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
                is_device_hidden TEXT,
                ime_data TEXT
            )
        """)

        #Create dimmerlight table
        self.cursor.execute("""
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
        """)

        #Create zwave_history table
        self.cursor.execute("""
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
        """)

        #Create automation table
        self.cursor.execute("""
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
        """)

        #Create automation table
        self.cursor.execute("""
            CREATE TABLE iqremotesettings (
                _id TEXT PRIMARY KEY,
                version TEXT,
                opr TEXT,
                partition_id TEXT,
                zone_id TEXT,
                mac_address TEXT,
                name TEXT,
                value TEXT
            )
        """)

        #Create doorlock table
        self.cursor.execute("""
            CREATE TABLE doorlock (
                _id TEXT PRIMARY KEY,
                version TEXT,
                opr TEXT,
                partition_id TEXT,
                doorlock_name TEXT,
                status TEXT,
                node_id TEXT,
                created_by TEXT,
                created_date TEXT,
                updated_by TEXT,
                last_updated_date TEXT,
                remote_arming TEXT,
                keyfob_arming TEXT,
                panel_arming TEXT,
                endpoint TEXT,
                paired_status TEXT
            )
        """)

        self.db.commit()
