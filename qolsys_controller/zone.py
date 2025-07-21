import logging

from qolsys_controller.exceptions import UnableToParseSensorException
from qolsys_controller.exceptions import UnknownQolsysSensorException
from qolsys_controller.observable import QolsysObservable
from qolsys_controller.partition import QolsysPartition
from qolsys_controller.utils import find_subclass

LOGGER = logging.getLogger(__name__)

class QolsysSensor(QolsysObservable):

    SENSOR_STATUS_ARRAY = ['Open', 'Closed', 'Active', 'Inactive','Activated','Idle','Unreachable','Tampered','Synchonizing']

    def __init__(self, sensor_id: str, sensorname: str, group: str, sensorstatus: str,
                 sensorstate: str, zone_id: int, zone_type: int,
                 zone_physical_type: int, zone_alarm_type: int,
                 partition_id: int,battery_status: str) -> None:
        super().__init__()

        self._id = sensor_id
        self._sensorname = sensorname
        self._group = group
        self._sensorstatus = sensorstatus
        self._sensorstate = sensorstate
        self._zone_id = zone_id
        self._zone_type = zone_type
        self._zone_physical_type = zone_physical_type
        self._zone_alarm_type = zone_alarm_type
        self._partition_id = partition_id
        self._battery_status = battery_status
        self._sensortts = ''
        self._latestdBm = ''
        self._averagedBm = ''
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
        self._time = ''

        self._NOTIFY_SENSORSTATUS = True
        self._NOTIFY_BATTERY_STATUS = True
        self._NOTIFY_SENSOR_NAME = True
        self._NOTIFY_PARTITION_ID = True
        self._NOTIFY_TIME = True
        
    @property
    def partition(self) -> QolsysPartition:
        return self._partition

    @partition.setter
    def partition(self, partition: QolsysPartition):
        self._partition = partition

    def update(self,contentValues:dict):
        # Check if we are updating same zoneid
        zone_id_update =contentValues.get('zoneid','')
        if int(zone_id_update) != int(self._zone_id):
            LOGGER.error(f"Updating zone '{self._zone_id}' ({self.sensorname}) with sensor '{zone_id_update}' (different id)")
            return
        
        # Update sensorsatus
        if 'sensorstatus' in contentValues:
            self.sensorstatus = contentValues.get('sensorstatus')

        # Update battery_status
        if 'battery_status' in contentValues:
            self.battery_status = contentValues.get('battery_status')

        # Update sensor_name
        if 'sensor_name' in contentValues:
            self.sensorname = contentValues.get('sensor_name')

        # Update time
        if 'time' in contentValues:
            self.time = contentValues.get('time')

        # Update partition_id
        if 'partition_id' in contentValues:
            self._partition_id = contentValues.get('partition_id')
        
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

    @sensorstatus.setter
    def sensorstatus(self, value):
        if value not in self.SENSOR_STATUS_ARRAY:
            LOGGER.debug(f"Sensor{self.zone_id} ({self._sensorname}) - Unknow sensorstatus {value}")

        if self._sensorstatus != value:
            LOGGER.debug(f"Zone{self._zone_id} ({self._sensorname}) - sensorstatus:{value}")
            self._sensorstatus = value
            if self._NOTIFY_SENSORSTATUS:
                self.notify()

    @battery_status.setter
    def battery_status(self, value):
        if self.battery_status != value:
            LOGGER.debug(f"Zone{self._zone_id} ({self._sensorname}) - battery_status:{value}")
            self.battery_status = value
            if self._NOTIFY_BATTERY_STATUS:
                self.notify()
    
    @sensorname.setter
    def sensorname(self, value):
        if self.sensorname != value:
            prev_value = self.sensorname
            self.sensorname = value
            if self.NOTIFY_UPDATE_SENSORNAME:
                self.notify()

    @time.setter
    def time(self, value):
        if self._time != value:
            LOGGER.debug(f"Zone{self._zone_id} ({self._sensorname}) - time:{value}")
            self._time = value
            if self._NOTIFY_TIME:
                self.notify()

    @partition_id.setter
    def partition_id(self, value):
        if self.partition_id != value:
            self.partition_id = value
            self.notify()

    def __str__(self):
        return (f"<{type(self).__name__} id={self.zone_id} name={self.sensorname} "
                f"group={self.group} status={self.sensorstatus} "
                f"state={self.sensorstate} zone_id={self.zone_id} "
                f"zone_type={self.zone_type} "
                f"zone_physical_type={self.zone_physical_type} "
                f"zone_alarm_type={self.zone_alarm_type} "
                f"partition_id={self.partition_id}>")

class _QolsysSensorWithoutUpdates(object):
    pass


class QolsysSensorDoorWindow(QolsysSensor):
    @classmethod
    def from_json(cls, data, partition, common=None):
        return cls.from_json_subclass('Door_Window', data, partition, common)


class QolsysSensorMotion(QolsysSensor):
    @classmethod
    def from_json(cls, data, partition, common=None):
        return cls.from_json_subclass('Motion', data, partition, common)


class QolsysSensorPanelMotion(QolsysSensorMotion):
    @classmethod
    def from_json(cls, data, partition, common=None):
        return cls.from_json_subclass('Panel Motion', data, partition, common)


class QolsysSensorGlassBreak(QolsysSensor):
    @classmethod
    def from_json(cls, data, partition, common=None):
        return cls.from_json_subclass('GlassBreak', data, partition, common)


class QolsysSensorPanelGlassBreak(QolsysSensorGlassBreak, _QolsysSensorWithoutUpdates):
    @classmethod
    def from_json(cls, data, partition, common=None):
        return cls.from_json_subclass('Panel Glass Break', data, partition, common)


class QolsysSensorBluetooth(QolsysSensor, _QolsysSensorWithoutUpdates):
    @classmethod
    def from_json(cls, data, partition, common=None):
        return cls.from_json_subclass('Bluetooth', data, partition, common)


class QolsysSensorSmokeDetector(QolsysSensor):
    @classmethod
    def from_json(cls, data, partition, common=None):
        return cls.from_json_subclass('SmokeDetector', data, partition, common)


class QolsysSensorCODetector(QolsysSensor):
    @classmethod
    def from_json(cls, data, partition, common=None):
        return cls.from_json_subclass('CODetector', data, partition, common)


class QolsysSensorWater(QolsysSensor):
    @classmethod
    def from_json(cls, data, partition, common=None):
        return cls.from_json_subclass('Water', data, partition, common)


class QolsysSensorFreeze(QolsysSensor):
    @classmethod
    def from_json(cls, data, partition, common=None):
        return cls.from_json_subclass('Freeze', data, partition, common)


class QolsysSensorHeat(QolsysSensor):
    @classmethod
    def from_json(cls, data, partition, common=None):
        return cls.from_json_subclass('Heat', data, partition, common)


class QolsysSensorTilt(QolsysSensor):
    @classmethod
    def from_json(cls, data, partition, common=None):
        return cls.from_json_subclass('Tilt', data, partition, common)


class QolsysSensorKeypad(QolsysSensor, _QolsysSensorWithoutUpdates):
    @classmethod
    def from_json(cls, data, partition, common=None):
        return cls.from_json_subclass('Keypad', data, partition, common)


class QolsysSensorAuxiliaryPendant(QolsysSensor, _QolsysSensorWithoutUpdates):
    @classmethod
    def from_json(cls, data, partition, common=None):
        return cls.from_json_subclass('Auxiliary Pendant', data, partition, common)


class QolsysSensorSiren(QolsysSensor, _QolsysSensorWithoutUpdates):
    @classmethod
    def from_json(cls, data, partition, common=None):
        return cls.from_json_subclass('Siren', data, partition, common)


class QolsysSensorKeyFob(QolsysSensor, _QolsysSensorWithoutUpdates):
    @classmethod
    def from_json(cls, data, partition, common=None):
        return cls.from_json_subclass('KeyFob', data, partition, common)


class QolsysSensorTemperature(QolsysSensor):
    @classmethod
    def from_json(cls, data, partition, common=None):
        return cls.from_json_subclass('Temperature', data, partition, common)


class QolsysSensorTakeoverModule(QolsysSensor, _QolsysSensorWithoutUpdates):
    @classmethod
    def from_json(cls, data, partition, common=None):
        return cls.from_json_subclass('TakeoverModule', data, partition, common)


class QolsysSensorTranslator(QolsysSensor, _QolsysSensorWithoutUpdates):
    @classmethod
    def from_json(cls, data, partition, common=None):
        return cls.from_json_subclass('Translator', data, partition, common)


class QolsysSensorDoorbell(QolsysSensor):
    @classmethod
    def from_json(cls, data, partition, common=None):
        return cls.from_json_subclass('Doorbell', data, partition, common)


class QolsysSensorShock(QolsysSensor):
    @classmethod
    def from_json(cls, data, partition, common=None):
        return cls.from_json_subclass('Shock', data, partition, common)