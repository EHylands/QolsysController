import logging

from qolsys_controller.observable import QolsysObservable
from qolsys_controller.partition import QolsysPartition

LOGGER = logging.getLogger(__name__)

class QolsysZone(QolsysObservable):

    ZONE_STATUS_ARRAY = ['Open', 'Closed', 'Active', 'Inactive','Activated','Idle','Unreachable','Tampered','Synchonizing','connected']
    ZONE_GROUP_ARRAY = ['Door_Window','Motion','Panel Motion','GlassBreak','Panel Glass Break','Bluetooth','SmokeDetector',
                        'CODetector','Water','Freeze','Heat','Tilt','Keypad','Auxiliary Pendant','Siren','KeyFob','Temperature',
                        'TakeoverModule','Translator','Doorbell','Shock']


    def __init__(self, sensor_id: str, 
                 sensorname: str, 
                 group: str, 
                 sensorstatus: str,
                 sensorstate: str, 
                 zone_id: int, 
                 zone_type: int,
                 zone_physical_type: int, 
                 zone_alarm_type: int,
                 partition_id: int,
                 battery_status: str,
                 sensortype:str,
                 latestdBm:str,
                 averagedBm:str,
                 time:str) -> None:
    
    #def __init__(self,data:dict):
        super().__init__()

        self._id =  sensor_id
        self._sensorname =  sensorname
        self._group =  group
        self._sensorstatus = sensorstatus
        self._sensorstate = sensorstate
        self._sensortype = sensortype
        self._zone_id = zone_id
        self._zone_type = zone_type
        self._zone_physical_type = zone_physical_type
        self._zone_alarm_type = zone_alarm_type
        self._partition_id = partition_id
        self._battery_status = battery_status
        self._sensortts = ''
        self._latestdBm = latestdBm
        self._averagedBm = averagedBm
        self._current_capability = ''
        self._zone_rf_sensor = ''
        self._zone_supervised = ''
        self._zone_reporting_enabled = ''
        self._zone_two_way_voice_enabled = ''
        self._signal_source = ''
        self._serial_number = ''
        self._chimetype = ''
        self._frame_count = ''
        self._frame_type = ''
        self._allowdisarming = ''
        self._time = time

        self._NOTIFY_SENSORSTATUS = True
        self._NOTIFY_BATTERY_STATUS = True
        self._NOTIFY_SENSOR_NAME = True
        self._NOTIFY_PARTITION_ID = True
        self._NOTIFY_TIME = False

        #self.update(data)
        
    def update(self,contentValues:dict):

        # Object creation
        if self.zone_id == '':
            self._zone_id = contentValues.get('zoneid')

        zone_id_update = contentValues.get('zoneid','')
        if int(zone_id_update) != int(self._zone_id):
           LOGGER.error(f"Updating zone '{self._zone_id}' ({self.sensorname}) with sensor '{zone_id_update}' (different id)")
           return
        
        self.start_batch_update()

         # Update sensor_name
        if 'sensorname' in contentValues:
            self.sensorname = contentValues.get('sensorname')
        
        # Update sensorsatus
        if 'sensorstatus' in contentValues:
            self.sensorstatus = contentValues.get('sensorstatus')

        # Update battery_status
        if 'battery_status' in contentValues:
            self.battery_status = contentValues.get('battery_status')

        # Update time
        if 'time' in contentValues:
            self.time = contentValues.get('time')

        # Update partition_id
        if 'partition_id' in contentValues:
            self._partition_id = contentValues.get('partition_id')

        # Update lastestdBm
        if 'lastestdBm' in contentValues:
            self.latestdBm = contentValues.get('latestdBm')

        # Update averagedBm
        if 'averagedBm' in contentValues:
            self.averagedBm = contentValues.get('averagedBm')

        if 'group' in contentValues:
            self._group = contentValues.get('group')

        if 'sensorstate' in contentValues:
            self._sensorstate = contentValues.get('sensorstate')

        if 'sensortype' in contentValues:
            self.sensortype = contentValues.get('sensortype')

        if 'zone_type' in contentValues:
            self._zone_type = contentValues.get('zone_type')

        if 'zone_physical_type' in contentValues:
            self._zone_physical_type = contentValues.get('zone_physical_type')

        if 'zone_alarm_type' in contentValues:
            self._zone_alarm_type = contentValues.get('zone_alarm_type')

        if 'sensorttss' in contentValues:
            self._sensortts = contentValues.get('sensortts')

        if 'current_capability' in contentValues:
            self._current_capability = contentValues.get('current_capability')

        if 'zone_rf_sensor' in contentValues:
            self._zone_rf_sensor = contentValues.get('zone_rf_sensor')

        if 'zone_supervised' in contentValues:
            self._zone_supervised = contentValues.get('zone_supervised')

        if 'zone_reporting_enabled' in contentValues:
            self._zone_reporting_enabled = contentValues.get('zone_reporting_enabled')

        if 'zone_two_way_voice_enabled' in contentValues:
            self._zone_two_way_voice_enabled = contentValues.get('zone_two_way_voice_enabled')

        if 'signal_source' in contentValues:
            self._signal_source = contentValues.get('signal_source')

        if 'serial_number' in contentValues:
            self._serial_number = contentValues.get('serial_number')
        
        if 'chimetype' in contentValues:
            self._chimetype = contentValues.get('chimetype')

        if 'frame_count' in contentValues:
            self._frame_count = contentValues.get('frame_count')
        
        if 'frame_type' in contentValues:
            self._frame_type = contentValues.get('frame_type')

        if 'allowdisarming' in contentValues:
            self._allowdisarming = contentValues.get('allowdisarming')

        self.end_batch_update()

    @property
    def id(self):
        return self._id
       
    @property
    def sensorname(self):
        return self._sensorname

    @property
    def group(self):
        return self._group

    @property
    def sensorstatus(self):
        return self._sensorstatus
    
    @property
    def battery_status(self):
        return self._battery_status

    @property
    def sensorstate(self):
        return self._sensorstate
    
    @property
    def sensortype(self):
        return self._sensortype

    @property
    def zone_id(self):
        return self._zone_id

    @property
    def zone_type(self):
        return self._zone_type

    @property
    def zone_physical_type(self):
        return self._zone_physical_type

    @property
    def zone_alarm_type(self):
        return self._zone_alarm_type

    @property
    def partition_id(self):
        return self._partition_id
    
    @property 
    def time(self):
        return self._time
    
    @property
    def partition_id(self):
        return self._partition_id
    
    @property
    def latestdBm(self):
        return self._latestdBm
    
    @property  
    def averagedBm(self):
        return self._averagedBm
    
    @averagedBm.setter
    def averagedBm(self,value):
        if self._averagedBm != value:
            self._averagedBm = value
            self.notify()
    
    @latestdBm.setter
    def latestdBm(self,value):
        if self._latestdBm != value:
            self.latestdBm = value
            self.notify()

    @sensorstatus.setter
    def sensorstatus(self, value):
        if value not in self.ZONE_STATUS_ARRAY:
            LOGGER.debug(f"Sensor{self.zone_id} ({self._sensorname}) - Unknow sensorstatus {value}")

        if self._sensorstatus != value:
            LOGGER.debug(f"Zone{self._zone_id} ({self._sensorname}) - sensorstatus: {value}")
            self._sensorstatus = value
            if self._NOTIFY_SENSORSTATUS:
                self.notify()

    @battery_status.setter
    def battery_status(self, value):
        if self._battery_status != value:
            LOGGER.debug(f"Zone{self._zone_id} ({self._sensorname}) - battery_status: {value}")
            self._battery_status = value
            if self._NOTIFY_BATTERY_STATUS:
                self.notify()
    
    @sensorname.setter
    def sensorname(self, value):
        if self.sensorname != value:
            self._sensorname = value
            self.notify()

    @time.setter
    def time(self, value):
        if self._time != value:
            LOGGER.debug(f"Zone{self._zone_id} ({self._sensorname}) - time: {value}")
            self._time = value
            if self._NOTIFY_TIME:
                self.notify()

    @sensortype.setter
    def sensortype(self,value):
        if self._sensortype != value:
            self._sensortype = value

    @partition_id.setter
    def partition_id(self, value):
        if self.partition_id != value:
            self.partition_id = value
            self.notify()   

    def to_dict(self) -> dict:
        return {
            '_id': self.id,
            'sensor_name': self.sensorname,
            'group': self.group,
            'sensorstatus': self.sensorstatus,
            'sensorstate': self.sensorstate,
            'sensortype': self.sensortype,
            'zoneid': self.zone_id,
            'zone_type': self.zone_type,
            'zone_physical_type': self.zone_physical_type,
            'zone_alarm_type': self.zone_alarm_type,
            'partition_id': self.partition_id,
            'battery_status': self.battery_status,
            'sensortts': self._sensortts,
            'latestdBm': self.latestdBm,
            'averagedBm': self.averagedBm,
            'current_capability': self._current_capability,
            'zone_rf_sensor': self._zone_rf_sensor,
            'zone_supervised': self._zone_supervised,
            'zone_reporting_enabled': self._zone_reporting_enabled,
            'zone_two_way_voice_enabled': self._zone_two_way_voice_enabled,
            'signal_source': self._signal_source,
            'serial_number': self._serial_number,
            'chimetype': self._chimetype,
            'frame_count': self._frame_count, 
            'frame_type': self._frame_type,
            'allowdisarming': self._allowdisarming,
            'time': self.time
        }

    def __str__(self):
        return (f"<{type(self).__name__} id={self.zone_id} name={self.sensorname} "
                f"group={self.group} status={self.sensorstatus} "
                f"state={self.sensorstate} zone_id={self.zone_id} "
                f"zone_type={self.zone_type} "
                f"zone_physical_type={self.zone_physical_type} "
                f"zone_alarm_type={self.zone_alarm_type} "
                f"partition_id={self.partition_id}>")