import logging

from .enum import ZoneSensorGroup, ZoneSensorType, ZoneStatus
from .observable import QolsysObservable

LOGGER = logging.getLogger(__name__)

class QolsysZone(QolsysObservable):

    def __init__(self, data:dict) -> None:
        super().__init__()

        self._zone_id = data.get("zoneid","")
        self._sensorname =  data.get("sensorname","")
        self._sensorstatus:ZoneStatus = ZoneStatus(data.get("sensorstatus",""))
        self._sensortype = ZoneSensorType(data.get("sensortype",""))
        self._sensorgroup =  data.get("sensorgroup","")
        self._battery_status = data.get("battery_status","")
        self._averagedBm = data.get("averagedBm","")
        self._latestdBm = data.get("latestdBm","")
        self._ac_status = data.get("ac_status","")

        self._id = data.get("_id","")
        self._zone_type = data.get("zone_type","")
        self._sensor_id = data.get("sensorid","")
        self._sensorstate = data.get("sensorstate","")
        self._zone_physical_type = data.get("zone_physical_type","")
        self._zone_alarm_type = data.get("zone_alarm_type","")
        self._partition_id = data.get("partition_id","")
        self._sensortts = data.get("sensortts","")
        self._current_capability = data.get("current_capability","")
        self._zone_rf_sensor = data.get("zone_rf_sensor","")
        self._zone_supervised = data.get("zone_supervised","")
        self._zone_reporting_enabled = data.get("zone_reporting_enabled","")
        self._zone_two_way_voice_enabled = data.get("zone_two_way_voice_enabled","")
        self._signal_source = data.get("signal_source","")
        self._serial_number = data.get("serial_number","")
        self._chimetype = data.get("chimetype","")
        self._frame_count = data.get("frame_count","")
        self._frame_type = data.get("frame_type","")
        self._frame_id = data.get("frame_id","")
        self._allowdisarming = data.get("allowdisarming","")
        self._time = data.get("time","")
        self._version = data.get("version","")
        self._opr = data.get("opr","")
        self._zone_equipement_code = data.get("zone_equipment_code","")
        self._created_date = data.get("created_date","")
        self._created_by = data.get("created_by","")
        self._updated_by = data.get("updated_by","")
        self._updated_date = data.get("updated_date","")
        self._shortID = data.get("shortID","")
        self._diag_24hr = data.get("diag_24hr","")
        self._device_capability = data.get("device_capability","")
        self._sub_type = data.get("sub_type","")
        self._powerg_manufacture_id = data.get("powerg_manufacture_id","")
        self._parent_node = data.get("parent_node","")
        self._extras = data.get("extras","")

    def update(self,data:dict) -> None:  # noqa: C901, PLR0912, PLR0915

        zone_id_update = data.get("zoneid","")
        if zone_id_update != self._zone_id:
           LOGGER.error("Updating Zone%s (%s) with Zone%s (different id)",self._zone_id,self.sensorname,zone_id_update)
           return

        self.start_batch_update()

         # Update sensor_name
        if "sensorname" in data:
            self.sensorname = data.get("sensorname")

        # Update sensorsatus
        if "sensorstatus" in data:
            self.sensorstatus = ZoneStatus(data.get("sensorstatus"))

        # Update battery_status
        if "battery_status" in data:
            self.battery_status = data.get("battery_status")

        # Update time
        if "time" in data:
            self.time = data.get("time")

        # Update partition_id
        if "partition_id" in data:
            self._partition_id = data.get("partition_id")

        # Update lastestdBm
        if "lastestdBm" in data:
            self.latestdBm = data.get("latestdBm")

        # Update averagedBm
        if "averagedBm" in data:
            self.averagedBm = data.get("averagedBm")

        if "sensorgroup" in data:
            self.sensorgroup = data.get("sensorgroup")

        if "sensorstate" in data:
            self._sensorstate = data.get("sensorstate")

        if "sensortype" in data:
            self.sensortype = ZoneSensorType(data.get("sensortype"))

        if "zone_type" in data:
            self._zone_type = data.get("zone_type")

        if "zone_physical_type" in data:
            self._zone_physical_type = data.get("zone_physical_type")

        if "zone_alarm_type" in data:
            self._zone_alarm_type = data.get("zone_alarm_type")

        if "sensorttss" in data:
            self._sensortts = data.get("sensortts")

        if "current_capability" in data:
            self._current_capability = data.get("current_capability")

        if "zone_rf_sensor" in data:
            self._zone_rf_sensor = data.get("zone_rf_sensor")

        if "zone_supervised" in data:
            self._zone_supervised = data.get("zone_supervised")

        if "zone_reporting_enabled" in data:
            self._zone_reporting_enabled = data.get("zone_reporting_enabled")

        if "zone_two_way_voice_enabled" in data:
            self._zone_two_way_voice_enabled = data.get("zone_two_way_voice_enabled")

        if "signal_source" in data:
            self._signal_source = data.get("signal_source")

        if "serial_number" in data:
            self._serial_number = data.get("serial_number")

        if "chimetype" in data:
            self._chimetype = data.get("chimetype")

        if "frame_count" in data:
            self._frame_count = data.get("frame_count")

        if "frame_type" in data:
            self._frame_type = data.get("frame_type")

        if "allowdisarming" in data:
            self._allowdisarming = data.get("allowdisarming")

        self.end_batch_update()

    @property
    def id(self) -> str:
        return self._id

    @property
    def sensorname(self) -> str:
        return self._sensorname

    @property
    def sensorgroup(self) -> str:
        return self._sensorgroup

    @property
    def sensorstatus(self) -> ZoneStatus:
        return self._sensorstatus

    @property
    def battery_status(self) -> str:
        return self._battery_status

    @property
    def sensorstate(self) -> str:
        return self._sensorstate

    @property
    def sensortype(self) -> ZoneSensorType:
        return self._sensortype

    @property
    def zone_id(self) -> str:
        return self._zone_id

    @property
    def zone_type(self) -> str:
        return self._zone_type

    @property
    def zone_physical_type(self) -> str:
        return self._zone_physical_type

    @property
    def zone_alarm_type(self) -> str:
        return self._zone_alarm_type

    @property
    def partition_id(self) -> str:
        return self._partition_id

    @property
    def time(self) -> str:
        return self._time

    @property
    def latestdBm(self)  -> str:
        return self._latestdBm

    @property
    def averagedBm(self) -> str:
        return self._averagedBm

    @averagedBm.setter
    def averagedBm(self,value:str) -> None:
        if self._averagedBm != value:
            self._averagedBm = value
            self.notify()

    @latestdBm.setter
    def latestdBm(self,value:str) -> None:
        if self._latestdBm != value:
            self.latestdBm = value
            self.notify()

    @sensorstatus.setter
    def sensorstatus(self, new_value:ZoneStatus) -> None:
        if self._sensorstatus != new_value:
            LOGGER.debug("Zone%s (%s) - sensorstatus: %s",self._zone_id,self.sensorname,new_value)
            self._sensorstatus = new_value
            self.notify()

    @battery_status.setter
    def battery_status(self, value:str) -> None:
        if self._battery_status != value:
            LOGGER.debug("Zone%s (%s) - battery_status: %s",self.zone_id,self.sensorname,value)
            self._battery_status = value
            self.notify()

    @sensorname.setter
    def sensorname(self, value:str) -> None:
        if self.sensorname != value:
            self._sensorname = value
            self.notify()

    @time.setter
    def time(self, value:str) -> None:
        if self._time != value:
            LOGGER.debug("Zone%s (%s) - time: %s",self.zone_id,self.sensorname,value)
            self._time = value
            self.notify()

    @sensortype.setter
    def sensortype(self,value:ZoneSensorType) -> None:
        if self._sensortype != value:
            self._sensortype = value
            self.notify()

    @sensorgroup.setter
    def sensorgroup(self,new_value:str) -> None:
        if self._sensorgroup != new_value:

            # Report new values
            try:
                ZoneSensorGroup(new_value)
            except ValueError:
                LOGGER.exception("Unknown Sensor group: %s, please report",new_value)

            self._sensorgroup = new_value
            LOGGER.debug("Zone%s (%s) - sensorgroup: %s",self.zone_id,self.sensorname,new_value.name)
            self.notify()

    @partition_id.setter
    def partition_id(self, value:str) -> None:
        if self.partition_id != value:
            self.partition_id = value
            self.notify()

    def to_dict(self) -> dict:
        return {
            "_id": self.id,
            "sensorid": self._sensor_id,
            "sensorname": self.sensorname,
            "sensorgroup": self.sensorgroup,
            "sensorstatus": self.sensorstatus.value,
            "sensorstate": self.sensorstate,
            "sensortype": self.sensortype.value,
            "zoneid": self.zone_id,
            "zone_type": self.zone_type,
            "zone_physical_type": self.zone_physical_type,
            "zone_alarm_type": self.zone_alarm_type,
            "partition_id": self.partition_id,
            "battery_status": self.battery_status,
            "sensortts": self._sensortts,
            "latestdBm": self.latestdBm,
            "averagedBm": self.averagedBm,
            "current_capability": self._current_capability,
            "zone_rf_sensor": self._zone_rf_sensor,
            "zone_supervised": self._zone_supervised,
            "zone_reporting_enabled": self._zone_reporting_enabled,
            "zone_two_way_voice_enabled": self._zone_two_way_voice_enabled,
            "signal_source": self._signal_source,
            "serial_number": self._serial_number,
            "chimetype": self._chimetype,
            "frame_count": self._frame_count,
            "frame_type": self._frame_type,
            "frame_id": self._frame_id,
            "allowdisarming": self._allowdisarming,
            "time": self.time,
            "version": self._version,
            "opr": self._opr,
            "zone_equipment_code": self._zone_equipement_code,
            "created_date": self._created_date,
            "created_by": self._created_by,
            "updated_by": self._updated_by,
            "updated_date": self._updated_date,
            "shortID": self._shortID,
            "diag_24hr": self._diag_24hr,
            "device_capability": self._device_capability,
            "sub_type": self._sub_type,
            "powerg_manufacture_id": self._powerg_manufacture_id,
            "parent_node": self._parent_node,
            "extras": self._extras,
            "ac_status": self._ac_status,
        }
